from rest_framework import viewsets
from lsdb.serializers import Location_pichinaSerializer
from lsdb.models import Location_pichina
from lsdb.permissions import ConfiguredPermission


class Location_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Location to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Location_pichina.objects.all()
    serializer_class = Location_pichinaSerializer
    permission_classes = [ConfiguredPermission]
