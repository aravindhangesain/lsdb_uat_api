from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import PermittedViewSerializer
from lsdb.models import PermittedView
from lsdb.permissions import ConfiguredPermission


class PermittedViewViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows PermissionType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = PermittedView.objects.all()
    serializer_class = PermittedViewSerializer
    permission_classes = [ConfiguredPermission]
