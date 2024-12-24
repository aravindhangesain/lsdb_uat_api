from rest_framework import viewsets

from lsdb.models import TestSequenceDefinition_pichina
from lsdb.permissions import ConfiguredPermission
from lsdb.serializers import TestSequenceDefinition_pichinaSerializer


class TestSequenceDefinition_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = TestSequenceDefinition_pichina.objects.all()
    serializer_class = TestSequenceDefinition_pichinaSerializer
    permission_classes = [ConfiguredPermission]