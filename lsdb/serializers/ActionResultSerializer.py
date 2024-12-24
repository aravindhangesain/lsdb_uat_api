from rest_framework import serializers
from lsdb.models import ActionResult
from lsdb.models import AzureFile
from lsdb.models import Group

from lsdb.serializers.AzureFileSerializer import AzureFileSerializer
from lsdb.serializers.GroupSerializer import GroupSerializer

# ProcedureResult...
class ActionResultSerializer(serializers.ModelSerializer):

    disposition_name = serializers.SerializerMethodField()
    action_definition_name = serializers.SerializerMethodField()
    parent_object = serializers.SerializerMethodField()
    completion_criteria = serializers.SerializerMethodField()
    attachments = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    groups = GroupSerializer(Group.objects.all(), many=True, read_only=True)


    def get_action_definition_name(self, obj):
        if obj.action_definition:
            return obj.action_definition.name
        else:
            return None

    def get_completion_criteria(self, obj):
        completion_response = []
        # print(obj.actioncompletionresult_set.all())
        for criterion in obj.actioncompletionresult_set.select_related('action_completion_definition').all():
            completion_response.append(
                {
                    'criteria_id':criterion.id,
                    "action_completion_definition":criterion.action_completion_definition.name,
                    "criteria_completed":criterion.criteria_completed,
                    "completed_datetime":criterion.completed_datetime,
                }
            )
        return completion_response
        # return obj.completion_criteria.all().values(
        #     "action_completion_definition",
        #     "criteria_completed",
        #     "completed_datetime",
        #     )

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_parent_object(self, obj):
        parent_object={
            'model': obj.content_type.model,
            'id': obj.content_object.id,
            'str': obj.content_object.__str__()
        }
        return parent_object

    class Meta:
        model = ActionResult
        fields = [
            'id',
            'url',
            'name',
            'description',
            'disposition',
            'disposition_name',
            'action_definition',
            'action_definition_name',
            'completion_criteria',
            'user',
            'execution_group',
            'done_datetime',
            'start_datetime',
            'promise_datetime',
            'eta_datetime',
            'parent_object',
            'groups',
            'attachments',
        ]
