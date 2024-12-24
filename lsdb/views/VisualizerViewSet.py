from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import VisualizerSerializer
from lsdb.models import Visualizer
from lsdb.permissions import ConfiguredPermission

# This code is a stub 
class VisualizerViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows Visualizer to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Visualizer.objects.all()
    serializer_class = VisualizerSerializer
    permission_classes = [ConfiguredPermission]
