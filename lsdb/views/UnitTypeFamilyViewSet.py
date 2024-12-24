from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import UnitTypeFamilySerializer
from lsdb.models import UnitTypeFamily
from lsdb.permissions import ConfiguredPermission


class UnitTypeFamilyViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows UnitTypeFamily to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UnitTypeFamily.objects.all()
    serializer_class = UnitTypeFamilySerializer
    permission_classes = [ConfiguredPermission]
