from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import AvailableDefectSerializer
from lsdb.models import AvailableDefect
from lsdb.permissions import ConfiguredPermission


class AvailableDefectViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows AvailableDefect to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AvailableDefect.objects.all()
    serializer_class = AvailableDefectSerializer
    permission_classes = [ConfiguredPermission]
