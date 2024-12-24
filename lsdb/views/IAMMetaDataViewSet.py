from rest_framework import viewsets
from lsdb.models import Unit
from lsdb.serializers import IAMMetaDataSerializer
from rest_framework import permissions
from lsdb.permissions import ConfiguredPermission

class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow only GET method
        return request.method == 'GET'

class IAMMetaDataViewSet(viewsets.ModelViewSet):
    logging_methods = ['GET']
    queryset = Unit.objects.all()
    serializer_class = IAMMetaDataSerializer
    lookup_field = 'serial_number'
    permission_classes = [ReadOnlyPermission, ConfiguredPermission]
