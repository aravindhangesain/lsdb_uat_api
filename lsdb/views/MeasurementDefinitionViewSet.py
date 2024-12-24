from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin

from django_filters import rest_framework as filters

from lsdb.serializers import MeasurementDefinitionSerializer
from lsdb.models import MeasurementDefinition
from lsdb.permissions import ConfiguredPermission

class MeasurementDefinitionFilter(filters.FilterSet):

    class Meta:
        model = MeasurementDefinition
        fields = {
            'name':['exact','icontains'],
            }

class MeasurementDefinitionViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows MeasurementDefinition to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementDefinition.objects.all()
    serializer_class = MeasurementDefinitionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MeasurementDefinitionFilter
    permission_classes = [ConfiguredPermission]
