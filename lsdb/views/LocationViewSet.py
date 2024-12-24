from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import LocationSerializer
from lsdb.models import Location
from lsdb.permissions import ConfiguredPermission


class LocationViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows Location to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [ConfiguredPermission]
