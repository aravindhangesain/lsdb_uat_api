from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import ConditionDefinitionSerializer
from lsdb.models import ConditionDefinition
from lsdb.permissions import ConfiguredPermission


class ConditionDefinitionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ConditionDefinitions to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ConditionDefinition.objects.all()
    serializer_class = ConditionDefinitionSerializer
    permission_classes = [ConfiguredPermission]
