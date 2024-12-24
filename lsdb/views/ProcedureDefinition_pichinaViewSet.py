from rest_framework import viewsets
from lsdb.serializers import ProcedureDefinition_pichinaSerializer
from lsdb.models import ProcedureDefinition_pichina
from lsdb.permissions import ConfiguredPermission

class ProcedureDefinition_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ProcedureDefinition to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ProcedureDefinition_pichina.objects.all()
    serializer_class = ProcedureDefinition_pichinaSerializer
    permission_classes = [ConfiguredPermission]

    