from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from django_filters import rest_framework as filters
from lsdb.serializers import Notetype_pichinaSerializer
from lsdb.models import Notetype_pichina
from lsdb.permissions import ConfiguredPermission

class NoteType_pichinaFilter(filters.FilterSet):
    class Meta:
        model = Notetype_pichina
        fields = [
            'groups__name',
        ]

class Notetype_PichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows NoteTypes to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Notetype_pichina.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = NoteType_pichinaFilter
    serializer_class = Notetype_pichinaSerializer
    permission_classes = [ConfiguredPermission]
