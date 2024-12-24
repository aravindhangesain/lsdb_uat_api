from rest_framework import viewsets
from lsdb.serializers import ModuleTechnology_pichinaSerializer
from lsdb.models import ModuleTechnology_pichina
from lsdb.permissions import ConfiguredPermission


class ModuleTechnology_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ModuleTechnology to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ModuleTechnology_pichina.objects.all()
    serializer_class = ModuleTechnology_pichinaSerializer
    permission_classes = [ConfiguredPermission]
