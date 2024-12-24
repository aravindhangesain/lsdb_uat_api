from rest_framework import viewsets
from lsdb.models import MeasurementResult_pichina


from lsdb.serializers import MeasurementResult_pichinaSerializer
from lsdb.permissions import ConfiguredPermission

class MeasurementResult_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementResult_pichina.objects.all()
    serializer_class = MeasurementResult_pichinaSerializer
    permission_classes = [ConfiguredPermission]

