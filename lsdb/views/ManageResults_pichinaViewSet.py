from rest_framework import viewsets
from lsdb.permissions import ConfiguredPermission
from lsdb.models import StepResult_pichina
from lsdb.serializers import StepResult_pichinaSerializer

class ManageResults_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepResult_pichina.objects.all()
    serializer_class = StepResult_pichinaSerializer
    permission_classes = [ConfiguredPermission]
