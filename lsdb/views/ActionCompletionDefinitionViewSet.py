import json
import pandas as pd
from django.db import IntegrityError, transaction
from django.db.models import Q, Max
from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.models import ActionDefinition
from lsdb.models import ActionCompletionDefinition

from lsdb.serializers import ActionCompletionDefinitionSerializer
from lsdb.permissions import ConfiguredPermission

class ActionCompletionDefinitionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ActionCompletionDefinitions to be created, viewed, or edited.
    """
    logging_methods = ['POST', 'PATCH', 'DELETE']
    queryset = ActionCompletionDefinition.objects.all()
    serializer_class = ActionCompletionDefinitionSerializer
    permission_classes = [ConfiguredPermission]
