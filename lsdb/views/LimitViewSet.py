from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import LimitSerializer
from lsdb.models import Limit
from lsdb.permissions import ConfiguredPermission


class LimitViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows Limit to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Limit.objects.all()
    serializer_class = LimitSerializer
    permission_classes = [ConfiguredPermission]
