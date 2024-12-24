from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from django_filters import rest_framework as filters
from lsdb.serializers import NoteTypeSerializer
from lsdb.models import NoteType
from lsdb.permissions import ConfiguredPermission

class NoteTypeFilter(filters.FilterSet):
    class Meta:
        model = NoteType
        fields = [
            'groups__name',
        ]

class NoteTypeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows NoteTypes to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = NoteType.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = NoteTypeFilter
    serializer_class = NoteTypeSerializer
    permission_classes = [ConfiguredPermission]
