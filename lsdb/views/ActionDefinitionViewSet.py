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
from lsdb.models import Group

from lsdb.serializers import ActionDefinitionSerializer
from lsdb.permissions import ConfiguredPermission

class ActionDefinitionFilter(filters.FilterSet):

    class Meta:
        model = ActionDefinition
        fields = [
            'name'
        ]

# ProcedureDefinitionViewset
class ActionDefinitionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ActionDefinitions to be created, viewed, or edited.
    Actions:
        set_completion_criteria
        set_groups
    """
    logging_methods = ['POST', 'PATCH', 'DELETE']
    queryset = ActionDefinition.objects.all()
    serializer_class = ActionDefinitionSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ActionDefinitionFilter

    @action(detail=True, methods=['get','post'])
    @transaction.atomic
    def set_groups(self, request, pk=None):
        """
        This action will set an ActionDefinition's group membership to the list sent.
        POST:
        {
            "groups":[ID,ID,ID]
        }
        """
        self.context={'request':request}
        action_definition = ActionDefinition.objects.get(id=pk)
        current_set = []
        for id in action_definition.group_set.all().values('id'):
            current_set.append(id.get('id'))
        if request.method == 'POST':
            params = request.data
            incoming_list = params.get('groups')
            # If there's an id in current_set that's not in the list:
            #    nuke it
            # If there's an id in the list that is not in current set:
            #    add it
            for group in current_set:
                if group not in incoming_list:
                    action_definition.group_set.remove(Group.objects.get(id=group))
            for group in incoming_list:
                if group not in current_set:
                    action_definition.group_set.add(Group.objects.get(id=group))
            return Response(ActionDefinitionSerializer(action_definition, many=False, context=self.context).data)
        else:
            # GET:
            return Response([])

    @action(detail=True, methods=['get','post'])
    @transaction.atomic
    def set_completion_criteria(self, request, pk=None):
        """
        This action will set an ActionDefinition's completion criteria list sent.
        POST:
        {
            "completion_criteria":[ID,ID,ID]
        }
        """
        self.context={'request':request}
        action_definition = ActionDefinition.objects.get(id=pk)
        current_set = []
        for id in action_definition.completion_criteria_set.all().values('id'):
            current_set.append(id.get('id'))
        if request.method == 'POST':
            params = request.data
            incoming_list = params.get('completion_criteria')
            for completion_criteria in current_set:
                if completion_criteria not in incoming_list:
                    action_definition.completion_criteria_set.remove(ActionCompletionDefinition.objects.get(id=completion_criteria))
            for completion_criteria in incoming_list:
                if completion_criteria not in current_set:
                    action_definition.completion_criteria_set.add(ActionCompletionDefinition.objects.get(id=completion_criteria))
            return Response(ActionDefinitionSerializer(action_definition, many=False, context=self.context).data)
        else:
            # GET:
            return Response([])
