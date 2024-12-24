from rest_framework import viewsets
from lsdb.serializers import ModuleProperty_pichinaSerializer
from lsdb.models import ModuleProperty_pichina
from lsdb.permissions import ConfiguredPermission


class ModuleProperty_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ModuleProperty to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ModuleProperty_pichina.objects.all()
    serializer_class = ModuleProperty_pichinaSerializer
    permission_classes = [ConfiguredPermission]
