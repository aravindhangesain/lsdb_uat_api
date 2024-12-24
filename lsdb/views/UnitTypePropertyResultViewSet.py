from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import UnitTypePropertyResultSerializer
from lsdb.models import UnitTypePropertyResult
from lsdb.permissions import ConfiguredPermission


class UnitTypePropertyResultViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows UnitTypePropertyResult to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UnitTypePropertyResult.objects.all()
    serializer_class = UnitTypePropertyResultSerializer
    permission_classes = [ConfiguredPermission]
