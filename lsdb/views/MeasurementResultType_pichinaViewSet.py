from rest_framework import viewsets
from lsdb.serializers import MeasurementResultType_pichinaSerializer
from lsdb.models import MeasurementResultType_pichina
from lsdb.permissions import ConfiguredPermission


class MeasurementResultType_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows MeasurementResultType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementResultType_pichina.objects.all()
    serializer_class = MeasurementResultType_pichinaSerializer
    permission_classes = [ConfiguredPermission]
