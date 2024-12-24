from django.apps import apps
from django.db import transaction
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.models import ActionDefinition
from lsdb.models import ActionResult
from lsdb.models import AzureFile
from lsdb.models import Disposition
from lsdb.models import Group
from lsdb.permissions import ConfiguredPermission
from lsdb.serializers import ActionResultSerializer
from lsdb.serializers.ActionResultReportSerializer import ActionResultReportSerializer
from lsdb.utils.ActionUtils import is_completion_criteria_complete, check_completion_criteria
from lsdb.views.PluginViewSet import _compile


class ActionResultFilter(filters.FilterSet):
    class Meta:
        model = ActionResult
        fields = [
            'groups',
            'groups__name'
        ]


class ActionResultViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ActionResults to be created, viewed, or edited.
    """
    logging_methods = ['POST', 'PATCH', 'DELETE']
    queryset = ActionResult.objects.all()
    serializer_class = ActionResultSerializer
    permission_classes = [ConfiguredPermission]

    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filterset_class = ActionResultFilter
    ordering_fields = ['eta_datetime']

    @transaction.atomic
    @action(detail=False, methods=['get', 'post'],
            serializer_class=ActionResultSerializer,
            )
    def new_action(self, request, pk=None):
        """
        This endpoint can be used to create a new ActionResult bucket that is not specifically tied
        to a ActionPlanDefinition. This is uncoupled from any parent objects.
        POST:
        {
                "name":"", Required
                "description":"",
                "disposition":$ID,Required
                "action_definition":$ID,Required
                "execution_group":"", optional
                "done_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "start_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "promise_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "eta_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "groups":[
                    ID(s)
                ],

                "parent_object":{ # REQUIRED
                    "model":"",required
                    "id":$ID,required
                }
       }
        """
        errors = []
        self.context = {'request': request}
        if request.method == 'POST':
            params = request.data
            disposition = params.get('disposition')
            if disposition and (type(disposition) == int):
                disposition = Disposition.objects.get(id=disposition)
            groups = params.get('groups')
            parent = params.get('parent_object')
            try:
                parent_model = apps.get_app_config('lsdb').get_model(parent.get('model'))
                parent_object = parent_model.objects.get(pk=parent.get('id'))
            except Exception as e:
                errors.append(
                    "Error: Parent object with model:{} and ID:{} not found".format(parent.get('model'),
                                                                                    parent.get('id'))
                )
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            action_definition = ActionDefinition.objects.get(id=params.get('action_definition'))
            action = ActionResult.objects.create(
                name=params.get('name'),
                description=params.get('description'),
                disposition=disposition,
                action_definition=action_definition,
                execution_group=params.get('execution_group'),
                done_datetime=params.get('done_datetime'),
                start_datetime=params.get('start_datetime'),
                promise_datetime=params.get('promise_datetime'),
                eta_datetime=params.get('eta_datetime'),
                content_object=parent_object
            )
            action.completion_criteria.set(action_definition.completion_criteria.all())
            if groups:
                for group in groups:
                    action.groups.add(Group.objects.get(id=group))
            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = ActionResultSerializer(action, many=False, context=self.context)
                # serializer = ActionResultSerializer([], many=False, context=self.context)
        else:  # GET
            serializer = ActionResultSerializer([], many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ActionResultSerializer,
            )
    def check_complete(self, request, pk=None):
        # Only execute the requested plugin if the criteria is not completed:
        self.context = {'request': request}
        result = ActionResult.objects.get(id=pk)
        response_dict = self._check_complete(result)
        return Response(response_dict)

    # This probably needs to move to utils/ActionUtils.py
    def _check_complete(self, result):
        """
        response_dict = {}
        for criterion in result.actioncompletionresult_set.all():
            if not criterion.criteria_completed:  # Criterion not done:
                plugin = Plugin.objects.get(name=criterion.action_completion_definition.plugin_name)
                params = json.loads(criterion.action_completion_definition.plugin_params)
                # print (params)
                for key in params.keys():
                    # print('key {}'.format(key))
                    try:
                        # params[key] = reduce( getattr, params[key].split('.'), result)
                        params[key] = reduce(getattr, params[key].split('.'), result)
                        # print('obj:{}'.format(params[key]))
                    except:
                        # The reduce failed, must just be a string...
                        pass
                errors, byte_code = self._compile(plugin)
                exec(byte_code)
                plugin_class = locals().get(plugin.name)
                plugin_instance = plugin_class()
                response_dict[criterion.action_completion_definition.name] = (
                        plugin_instance._run(**params) == criterion.action_completion_definition.expected_result)
                criterion.criteria_completed = response_dict[criterion.action_completion_definition.name]
                criterion.completed_datetime = timezone.now()
                criterion.save()
        return response_dict
        """
        return check_completion_criteria(result, result.actioncompletionresult_set.all(), _compile)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ActionResultSerializer,
            )
    def mark_complete(self, request, pk=None):
        """
        This endpoint can be used to mark an ActionResult bucket as completed. It checks  the criteria
        before it marks the action done, and will respond with a 400
        POST:
        {}

        OVERRIDE POST:
        {
            "override": boolean,
            "description": str,
        }
        """
        self.context = {'request': request}
        if request.method == 'POST':
            queryset = ActionResult.objects.get(id=pk)
            params = request.data
            if params.get('override'):
                queryset.done_datetime = timezone.now()
                queryset.user = request.user
                queryset.override_datetime = timezone.now()
                queryset.override_user = request.user
                queryset.override_description = params.get('description')
                queryset.disposition = Disposition.objects.get(id=20)
                queryset.save()
                serializer = self.serializer_class(queryset, many=False, context=self.context)
                return Response(serializer.data)
            else:
                response_dict = self._check_complete(queryset)
                if not is_completion_criteria_complete(response_dict.values()):
                    return Response('Error: action criteria not completed', status=status.HTTP_400_BAD_REQUEST)
                else:
                    queryset.done_datetime = timezone.now()
                    queryset.user = request.user
                    queryset.disposition = Disposition.objects.get(id=20)
                    queryset.save()
                serializer = self.serializer_class(queryset, many=False, context=self.context)
                return Response(serializer.data)
        else:
            return Response([])

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ActionResultSerializer,
            )
    def revoke(self, request, pk=None):
        """
        This endpoint can be used to mark an ActionResult revoked. Marking an
        ActionResult revoked causes it to be counted as complete.

        Revoked ActionResults should not be counted in reports, revenue, etc.

        POST:
        {
            "description": str,
        }
        """
        self.context = {'request': request}
        if request.method == 'POST':
            queryset = ActionResult.objects.get(id=pk)
            params = request.data
            queryset.done_datetime = timezone.now()
            queryset.user = request.user
            queryset.override_datetime = timezone.now()
            queryset.override_user = request.user
            queryset.override_description = params.get('description')
            queryset.disposition = Disposition.objects.get(id=14)
            queryset.save()
            serializer = self.serializer_class(queryset, many=False, context=self.context)
            return Response(serializer.data)
        else:
            return Response([])

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ActionResultSerializer,
            )
    def link_files(self, request, pk=None):
        """
        This action will link an existing AzureFile to this action_result.
        POST: {"id":1} to link azurfefile id=1 to this action_result
        """
        self.context = {'request': request}
        queryset = ActionResult.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            file_id = params.get('id')
            if file_id:
                attachment = AzureFile.objects.get(id=int(file_id))
                queryset.attachments.add(attachment)
                queryset.save()
        serializer = self.serializer_class(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], serializer_class=ActionResultReportSerializer)
    def reports(self, request):
        queryset = ActionResult.objects.filter(groups__name='Report Writers').order_by("eta_datetime")
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)


"""
"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format"
disp = Disposition.objects.get(name__iexact='available')
action_def = ActionDefinition.objects.get(id=1)
project = Project.objects.filter(number__icontains="test").first()
action = ActionResult.objects.create(
    name = 'test result',
    description = "test result description",
    disposition = disp,
    action_definition = action_def,
    execution_group = 1,
    eta_datetime = "2021-11-13 12:00-08:00",
    content_object = project,
)

{
    "name":"Workorder NTP",
    "description":"action workorder test",
    "disposition": 16,
    "action_definition":2,
    "execution_group" : 1,
    "eta_datetime":"2021-11-13 12:00-08:00"
}

{
    "name":"Projct action",
    "description":"action workorder test",
    "disposition": 16,
    "action_definition":1,
    "execution_group" : 1,
    "eta_datetime":"2021-11-13 12:00-08:00"
}
{
    "name":"Projcet Has Workorders",
    "description":"action workorder test",
    "disposition": 16,
    "action_definition":2,
    "execution_group" : 2,
    "eta_datetime":"2021-11-13 12:00-08:00"
}
# groups = params.get('groups'),
# attachments = params.get('attachments'),
# This is to try to preempt the multi-inheretance later.
# content_type =
# object_id =
# content_object =
# done_datetime = params.get('done_datetime'),
# start_datetime = params.get('start_datetime'),
# promise_datetime = params.get('promise_datetime'),
# completion_criteria =
# user =
"""
