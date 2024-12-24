from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.serializers import AssetCapacitySerializer
from lsdb.models import AssetCapacity
from lsdb.permissions import ConfiguredPermission

class AssetCapacityViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows AssetCapacity to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCapacity.objects.all()
    serializer_class = AssetCapacitySerializer
    permission_classes = [ConfiguredPermission]
