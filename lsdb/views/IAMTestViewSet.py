from rest_framework import viewsets
from lsdb.models import Unit
from lsdb.serializers import IAMTestSerializer
from rest_framework import permissions

class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow only GET method
        return request.method == 'GET'

class IAMTestViewSet(viewsets.ModelViewSet):
    logging_methods = ['GET']
    queryset = Unit.objects.all()
    serializer_class = IAMTestSerializer
    lookup_field = 'serial_number'
    permission_classes = [ReadOnlyPermission]

