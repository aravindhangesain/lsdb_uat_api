from django.db import IntegrityError, transaction

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.decorators import action

from lsdb.models import FileFormat
from lsdb.serializers import FileFormatSerializer
from lsdb.permissions import ConfiguredPermission, IsAdmin, GroupPermission


class FileFormatViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows a Template to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = FileFormat.objects.all()
    serializer_class = FileFormatSerializer
    permission_classes = [ConfiguredPermission]
