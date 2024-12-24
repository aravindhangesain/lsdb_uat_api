from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import ModulePropertySerializer
from lsdb.models import ModuleProperty
from lsdb.permissions import ConfiguredPermission


class ModulePropertyViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ModuleProperty to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ModuleProperty.objects.all()
    serializer_class = ModulePropertySerializer
    permission_classes = [ConfiguredPermission]
