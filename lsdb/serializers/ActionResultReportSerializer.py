from rest_framework import serializers

from lsdb.models import ActionResult
from lsdb.utils.ActionUtils import check_completion_criteria, is_completion_criteria_complete
from lsdb.views.PluginViewSet import _compile


class ActionResultReportSerializer(serializers.ModelSerializer):
    disposition = serializers.ReadOnlyField(source='disposition.name')
    action_definition = serializers.ReadOnlyField(source='action_definition.name')
    parent = serializers.SerializerMethodField()
    is_data_ready = serializers.SerializerMethodField()

    def get_parent(self, obj):
        return {
            "type": obj.content_type.model.capitalize(),
            "id": obj.object_id,
            "str": obj.content_object.__str__()
        }

    def get_is_data_ready(self, obj):
        completion_criteria_status = check_completion_criteria(obj, obj.actioncompletionresult_set.all(), _compile)
        return is_completion_criteria_complete(completion_criteria_status.values())

    class Meta:
        model = ActionResult
        fields = [
            'id',
            'name',
            'disposition',
            'action_definition',
            'start_datetime',
            'promise_datetime',
            'eta_datetime',
            'parent',
            'is_data_ready'
        ]
