import json

from django.apps import apps
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_400_BAD_REQUEST)
from rest_framework_tracking.mixins import LoggingMixin
import csv
from django.http import HttpResponse
from rest_framework.decorators import action

from lsdb.models import AzureFile
from lsdb.models import Disposition
from lsdb.models import DispositionCode
from lsdb.models import Label
from lsdb.models import Note_pichina
from lsdb.models import NoteReadStatus
from lsdb.models import NoteType
from lsdb.models import ProcedureResult
from lsdb.models import Unit
from lsdb.permissions import ConfiguredPermission
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.serializers import Note_pichinaSerializer
from lsdb.utils.NoteUtils import get_note_link
from lsdb.utils.Notification import Notification

class Note_pichinaFilter(filters.FilterSet):
    class Meta:
        model = Note_pichina
        fields = [
            'note_type__groups__name',
        ]


class Note_pichinaViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Notes to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Note_pichina.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = Note_pichinaFilter
    serializer_class = Note_pichinaSerializer

    @action(detail=False, methods=['get'])
    def flags(self, request):
        flags = Note_pichina.objects.filter(note_type__id=3).distinct()
        flags = flags.exclude(disposition__complete=True)
        serializer = self.get_serializer(flags, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def get_children(self, request, pk=None):
        self.context = {'request': request}

        notes = Note_pichina.objects.filter(parent_note__id=pk).order_by("datetime")
        serializer = self.serializer_class(notes, many=True, context=self.context)

        return Response(serializer.data)