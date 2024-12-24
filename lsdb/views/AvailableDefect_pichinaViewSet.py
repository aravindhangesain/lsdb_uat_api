from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import AvailableDefect_pichinaSerializer
from lsdb.models import AvailableDefect, AvailableDefect_pichina
from lsdb.permissions import ConfiguredPermission


class AvailableDefect_pichinaViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows AvailableDefect to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AvailableDefect_pichina.objects.all()
    serializer_class = AvailableDefect_pichinaSerializer
    permission_classes = [ConfiguredPermission]
