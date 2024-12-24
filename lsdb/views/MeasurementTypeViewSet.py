from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import MeasurementTypeSerializer
from lsdb.models import MeasurementType
from lsdb.permissions import ConfiguredPermission


class MeasurementTypeViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows MeasurementType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementType.objects.all()
    serializer_class = MeasurementTypeSerializer
    permission_classes = [ConfiguredPermission]
