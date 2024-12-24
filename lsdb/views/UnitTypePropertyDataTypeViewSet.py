from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import UnitTypePropertyDataTypeSerializer
from lsdb.models import UnitTypePropertyDataType
from lsdb.permissions import ConfiguredPermission


class UnitTypePropertyDataTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows UnitTypePropertyDataType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UnitTypePropertyDataType.objects.all()
    serializer_class = UnitTypePropertyDataTypeSerializer
    permission_classes = [ConfiguredPermission]
