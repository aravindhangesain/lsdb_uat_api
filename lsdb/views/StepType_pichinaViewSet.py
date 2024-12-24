from rest_framework import viewsets
from lsdb.serializers import StepType_pichinaSerializer
from lsdb.models import StepType_pichina
from lsdb.permissions import ConfiguredPermission


class StepType_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows StepTypes to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepType_pichina.objects.all()
    serializer_class = StepType_pichinaSerializer
    permission_classes = [ConfiguredPermission]
