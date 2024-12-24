from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import MeasurementResultTypeSerializer
from lsdb.models import MeasurementResultType
from lsdb.permissions import ConfiguredPermission


class MeasurementResultTypeViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows MeasurementResultType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementResultType.objects.all()
    serializer_class = MeasurementResultTypeSerializer
    permission_classes = [ConfiguredPermission]
