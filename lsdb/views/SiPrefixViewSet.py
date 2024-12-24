from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import SiPrefixSerializer
from lsdb.models import SiPrefix
from lsdb.permissions import ConfiguredPermission


class SiPrefixViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows SiPrefix to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = SiPrefix.objects.all()
    serializer_class = SiPrefixSerializer
    permission_classes = [ConfiguredPermission]
