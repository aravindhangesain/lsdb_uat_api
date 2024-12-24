from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import ModuleTechnologySerializer
from lsdb.models import ModuleTechnology
from lsdb.permissions import ConfiguredPermission


class ModuleTechnologyViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ModuleTechnology to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ModuleTechnology.objects.all()
    serializer_class = ModuleTechnologySerializer
    permission_classes = [ConfiguredPermission]
