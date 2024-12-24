import magic
from django.http import FileResponse, HttpResponse
from django_filters import rest_framework as filters

from rest_framework import viewsets
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
