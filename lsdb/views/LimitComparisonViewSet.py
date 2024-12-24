from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import LimitComparisonSerializer
from lsdb.models import LimitComparison
from lsdb.permissions import ConfiguredPermission


class LimitComparisonViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows LimitComparison to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = LimitComparison.objects.all()
    serializer_class = LimitComparisonSerializer
    permission_classes = [ConfiguredPermission]
