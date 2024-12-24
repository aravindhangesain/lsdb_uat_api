from rest_framework import viewsets
# from rest_framework_tracking.mixins import LoggingMixin
# from django_filters import rest_framework as filters

from lsdb.serializers import MeasurementDefinition_pichinaSerializer
from lsdb.models import MeasurementDefinition_pichina
from lsdb.permissions import ConfiguredPermission

# class MeasurementDefinitionFilter(filters.FilterSet):

#     class Meta:
#         model = MeasurementDefinition
#         fields = {
#             'name':['exact','icontains'],
#             }

class MeasurementDefinition_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows MeasurementDefinition to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementDefinition_pichina.objects.all()
    serializer_class = MeasurementDefinition_pichinaSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_class = MeasurementDefinitionFilter
    permission_classes = [ConfiguredPermission]
