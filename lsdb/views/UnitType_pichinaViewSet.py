from rest_framework import viewsets
from lsdb.models import UnitType_pichina
from lsdb.serializers import UnitType_pichinaSerializer


class UnitType_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UnitType_pichina.objects.all()
    serializer_class = UnitType_pichinaSerializer