from rest_framework import viewsets
from lsdb.serializers import ExpectedUnitType_pichinaSerializer
from lsdb.models import ExpectedUnitType_pichina
from lsdb.permissions import ConfiguredPermission


class ExpectedUnitType_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ExpectedUnitType_pichina.objects.all()
    serializer_class = ExpectedUnitType_pichinaSerializer
    permission_classes = [ConfiguredPermission]
