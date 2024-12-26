from urllib import response
import magic
from django.http import HttpResponse
from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework_tracking.mixins import LoggingMixin

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from azure.storage.blob import BlobServiceClient


from lsdb.models import AzureFile_pichina
from lsdb.serializers import AzureFile_pichinaSerializer
from lsdb.permissions import ConfiguredPermission
from lsdb.utils.Crypto import encrypt, decrypt

class AzureFileFilter(filters.FilterSet):
    # uploaded_min_datetime = filters.DateFromToRangeFilter(field_name='uploaded_datetime',lookup_expr='gte')
    # uploaded_max_datetime = filters.DateFromToRangeFilter(field_name='uploaded_datetime',lookup_expr='lte')
    uploaded_datetime = filters.DateFromToRangeFilter()
    class Meta:
        model = AzureFile_pichina
        # fields = {
        #     'name':['exact','icontains'],
        #     'uploaded_datetime',
        #     }
        fields = ['name','uploaded_datetime',]

class AzureFile_pichinaViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows AzureFile to be viewed or edited.
    Filters:
    uploaded_datetime_before
    uploaded_datetime_after
    Usage: `/api/1.0/azure_files/?uploaded_datetime_after=2021-03-01&uploaded_datetime_before=2021-03-20`
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AzureFile_pichina.objects.all()
    serializer_class = AzureFile_pichinaSerializer
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
        return super(AzureFile_pichinaViewSet, self)._clean_data(data)

    @action(detail=True, methods=['get'],
        # renderer_classes=(BinaryFileRenderer,),
        permission_classes=(ConfiguredPermission,),
        )
    def download(self, request, pk=None):
        try:
            file_record = AzureFile_pichina.objects.get(id=pk)
            blob_name = file_record.file.name
            container_name = 'testmedia1'
            connection_string = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_data = blob_client.download_blob()
            file_content = blob_data.readall()
            mime_type = magic.Magic(mime=True).from_buffer(file_content)
            response = HttpResponse(file_content, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{blob_name.split("/")[-1]}"'
            return response
        except AzureFile_pichina.DoesNotExist:
            return HttpResponse("File not found", status=404)
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

    @action(detail=True, methods=['get'],
        # renderer_classes=(BinaryFileRenderer,),
        permission_classes=(ConfiguredPermission,),
        )
    def get_magic_link(self, request, pk=None):
        # The user has permission to get here, so I will send a link
        self.context = {'request':request}
        azurefile = AzureFile_pichina.objects.get(pk=pk)
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
