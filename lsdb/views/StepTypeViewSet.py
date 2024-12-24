from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import StepTypeSerializer
from lsdb.models import StepType
from lsdb.permissions import ConfiguredPermission


class StepTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows StepTypes to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepType.objects.all()
    serializer_class = StepTypeSerializer
    permission_classes = [ConfiguredPermission]
