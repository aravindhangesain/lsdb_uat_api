from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.serializers import DispositionSerializer
from lsdb.models import Disposition
from lsdb.permissions import ConfiguredPermission


class DispositionFilter(filters.FilterSet):

    class Meta:
        model = Disposition
        fields = [
            'name',
            ]

class DispositionViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows Dispositions to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Disposition.objects.all()
    serializer_class = DispositionSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = DispositionFilter
