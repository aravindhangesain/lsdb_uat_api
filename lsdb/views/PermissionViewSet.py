from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import PermissionSerializer
from lsdb.models import Permission
from lsdb.permissions import ConfiguredPermission


class PermissionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Permission to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [ConfiguredPermission]
