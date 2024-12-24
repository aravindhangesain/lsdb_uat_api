from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import UnitTypePropertyTypeSerializer
from lsdb.models import UnitTypePropertyType
from lsdb.permissions import ConfiguredPermission


class UnitTypePropertyTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows UnitTypePropertyType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UnitTypePropertyType.objects.all()
    serializer_class = UnitTypePropertyTypeSerializer
    permission_classes = [ConfiguredPermission]
