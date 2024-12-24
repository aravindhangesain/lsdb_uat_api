from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import PermissionTypeSerializer
from lsdb.models import PermissionType
from lsdb.permissions import ConfiguredPermission


class PermissionTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows PermissionType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = PermissionType.objects.all()
    serializer_class = PermissionTypeSerializer
    permission_classes = [ConfiguredPermission]
