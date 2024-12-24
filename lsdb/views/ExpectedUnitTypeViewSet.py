from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import ExpectedUnitTypeSerializer
from lsdb.models import ExpectedUnitType
from lsdb.permissions import ConfiguredPermission


class ExpectedUnitTypeViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows ExpectedUnitType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ExpectedUnitType.objects.all()
    serializer_class = ExpectedUnitTypeSerializer
    permission_classes = [ConfiguredPermission]
