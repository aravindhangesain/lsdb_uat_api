from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import LimitComparisonModeSerializer
from lsdb.models import LimitComparisonMode
from lsdb.permissions import ConfiguredPermission


class LimitComparisonModeViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows LimitComparisonMode to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = LimitComparisonMode.objects.all()
    serializer_class = LimitComparisonModeSerializer
    permission_classes = [ConfiguredPermission]
