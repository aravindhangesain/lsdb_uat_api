from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin

from django_filters import rest_framework as filters

from lsdb.serializers import StepDefinitionSerializer
from lsdb.models import StepDefinition
from lsdb.permissions import ConfiguredPermission

class StepDefinitionFilter(filters.FilterSet):

    class Meta:
        model = StepDefinition
        fields = {
            'name':['exact','icontains'],
            }

class StepDefinitionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows StepDefinitions to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepDefinition.objects.all()
    serializer_class = StepDefinitionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StepDefinitionFilter
    permission_classes = [ConfiguredPermission]
