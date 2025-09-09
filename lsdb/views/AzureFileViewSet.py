from urllib import response
import magic
from django.http import FileResponse, HttpResponse
from django_filters import rest_framework as filters

from rest_framework import viewsets
from pathlib import Path
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework_tracking.mixins import LoggingMixin

from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny

from lsdb.models import AzureFile
from lsdb.serializers import AzureFileSerializer
from lsdb.permissions import ConfiguredPermission
from lsdb.utils.Crypto import encrypt, decrypt
from lsdb.models import *
from lsdb.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from django.core.mail import EmailMessage
import csv
from django.http import HttpResponse

class AzureFileFilter(filters.FilterSet):
    # uploaded_min_datetime = filters.DateFromToRangeFilter(field_name='uploaded_datetime',lookup_expr='gte')
    # uploaded_max_datetime = filters.DateFromToRangeFilter(field_name='uploaded_datetime',lookup_expr='lte')
    uploaded_datetime = filters.DateFromToRangeFilter()
    class Meta:
        model = AzureFile
        # fields = {
        #     'name':['exact','icontains'],
        #     'uploaded_datetime',
        #     }
        fields = ['name','uploaded_datetime',]

class AzureFileViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows AzureFile to be viewed or edited.
    Filters:
    uploaded_datetime_before
    uploaded_datetime_after
    Usage: `/api/1.0/azure_files/?uploaded_datetime_after=2021-03-01&uploaded_datetime_before=2021-03-20`
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AzureFile.objects.all()
    serializer_class = AzureFileSerializer
    parser_class = (FileUploadParser,)
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AzureFileFilter

    # Override _clean_data to decode data with ignore instead of replace to ignore
    # errors in decode so when the logger inserts the data to db, it will not hit
    # any decoding/encoding issues
    def _clean_data(self, data):
        if isinstance(data, bytes):
            # data = data.decode(errors='ignore')
            data = 'CLEANED FILE DATA'
        return super(AzureFileViewSet, self)._clean_data(data)

    @action(detail=True, methods=['get'],
        # renderer_classes=(BinaryFileRenderer,),
        permission_classes=(ConfiguredPermission,),
        )
    def download(self, request, pk=None):
        queryset = AzureFile.objects.get(id=pk)
        file = queryset.file
        file_handle = file.open()
        content_type = magic.from_buffer(file_handle.read(2048), mime=True)

        response = HttpResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename={0}'.format(file)
        return response

    @action(detail=True, methods=['get'],
            permission_classes=(ConfiguredPermission,))
    def custom_download(self, request, pk=None):
        queryset = AzureFile.objects.get(id=pk)
        file = queryset.file
        file_handle = file.open()
        content_type = magic.from_buffer(file_handle.read(2048), mime=True)
        file_handle.seek(0)
        save_path = Path("C:/pvel/documents")
        save_path.mkdir(parents=True, exist_ok=True)
        local_filename = save_path / file.name
        with open(local_filename, 'wb') as local_file:
            local_file.write(file_handle.read())
        file_handle.seek(0)
        response = HttpResponse(file_handle, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file.name}"'
        return response

    @action(detail=True, methods=['get'],
        # renderer_classes=(BinaryFileRenderer,),
        permission_classes=(ConfiguredPermission,),
        )
    def get_magic_link(self, request, pk=None):
        # The user has permission to get here, so I will send a link
        self.context = {'request':request}
        azurefile = AzureFile.objects.get(pk=pk)
        token = Token.objects.get(user = request.user)
        encrypted = encrypt(token.key)
        # print(encrypted, azurefile.url)
        # tokens = Token.objects.all()
        # print(tokens)
        response = HttpResponse([{'token':'{}'.format(encrypted)}])
        return response

    @action(detail=True, methods=['get'],
        # renderer_classes=(BinaryFileRenderer,),
        permission_classes=(AllowAny,),
        )
    def get_file(self, request, pk=None):
        # This endpoint has no permissions so we need to handle it ourselves
        self.context = {'request':request}
        encrypted = request.query_params.get('token')
        if encrypted:
            try:
                # this should be using Authenticate
                token = Token.objects.get(key = decrypt(encrypted))
                print('gotcha!')
            except :
                print('odd')
        return response
    
    @transaction.atomic
    @action(detail=False, methods=['get','post'])
    def create_subasset_by_fileupload(self, request):
        """
        This API is to create SubAssets from a CSV file upload.
        Please adhere to the below mentioned column names for successful upload:

        1. sub_asset_name
        2. description
        3. last_calibrated_date (format: YYYY-MM-DD)
        4. next_calibration (in days)
        """
        file = request.FILES.get('file')
        if not file:
            return Response(
                {"status": "error", "msg": "No file uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            decoded_file = file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            required_columns = [
                "sub_asset_name",
                
                "description",
                "last_calibrated_date",
                "next_calibration"
            ]

            for col in required_columns:
                if col not in reader.fieldnames:
                    return Response(
                        {"status": "error", "msg": f"Missing column: {col}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            created, skipped = [], []

            for row in reader:
                try:
                    sub_asset_name = row.get("sub_asset_name")
                    # asset_number = row.get("asset_number")

                    if SubAsset.objects.filter(
                        sub_asset_name=sub_asset_name
                    ).exists():
                        skipped.append(sub_asset_name)
                        continue

                    subasset = SubAsset(
                        sub_asset_name=sub_asset_name,
                    
                        description=row.get("description") or None,
                        last_calibrated_date=row.get("last_calibrated_date") or None,
                        next_calibration=row.get("next_calibration") or None,
                    )
                    subasset.save()
                    created.append(sub_asset_name)
                except Exception as e:
                    skipped.append(f"{row.get('sub_asset_name')} (error: {str(e)})")

            return Response(
                {
                    "status": "success",
                    "created": created,
                    "skipped": skipped
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"status": "error", "msg": f"Invalid file format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
