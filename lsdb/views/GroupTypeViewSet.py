from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import GroupTypeSerializer
from lsdb.models import GroupType
from lsdb.permissions import ConfiguredPermission


class GroupTypeViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows GroupType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = GroupType.objects.all()
    serializer_class = GroupTypeSerializer
    permission_classes = [ConfiguredPermission]
