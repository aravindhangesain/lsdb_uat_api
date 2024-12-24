from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin

from django_filters import rest_framework as filters

from lsdb.serializers import AssetTypeSerializer
from lsdb.models import AssetType
from lsdb.permissions import ConfiguredPermission

class AssetTypeFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = AssetType
        fields = [
            'name',
        ]

class AssetTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows AssetType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetType.objects.all()
    serializer_class = AssetTypeSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssetTypeFilter
