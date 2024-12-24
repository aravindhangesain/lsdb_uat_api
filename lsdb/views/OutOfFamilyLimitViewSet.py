# This Viewset is obsolete and is left here for historical reference only
from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import OutOfFamilyLimitSerializer
from lsdb.models import OutOfFamilyLimit
from lsdb.permissions import ConfiguredPermission


class OutOfFamilyLimitViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows OutOfFamilyLimit to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = OutOfFamilyLimit.objects.all()
    serializer_class = OutOfFamilyLimitSerializer
    permission_classes = [ConfiguredPermission]
