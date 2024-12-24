from rest_framework import viewsets
from lsdb.serializers import MeasurementType_pichinaSerializer
from lsdb.models import MeasurementType_pichina
from lsdb.permissions import ConfiguredPermission


class MeasurementType_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows MeasurementType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementType_pichina.objects.all()
    serializer_class = MeasurementType_pichinaSerializer
    permission_classes = [ConfiguredPermission]
