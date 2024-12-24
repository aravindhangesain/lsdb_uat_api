from rest_framework import viewsets

from lsdb.serializers import StepDefinition_pichinaSerializer
from lsdb.models import StepDefinition_pichina
from lsdb.permissions import ConfiguredPermission


class StepDefinition_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows StepDefinitions to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepDefinition_pichina.objects.all()
    serializer_class = StepDefinition_pichinaSerializer
    permission_classes = [ConfiguredPermission]
