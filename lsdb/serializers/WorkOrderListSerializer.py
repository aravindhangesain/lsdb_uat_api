from rest_framework import serializers
from django.db.models import Max
from lsdb.models import MeasurementResult
from lsdb.models import WorkOrder
from lsdb.serializers.TestSequenceDefinitionSerializer import TestSequenceDefinitionSerializer

class WorkOrderListSerializer(serializers.HyperlinkedModelSerializer):
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    test_sequence_definitions = TestSequenceDefinitionSerializer(many=True, read_only=True)
    last_action_datetime = serializers.SerializerMethodField()

    def get_last_action_datetime(self, obj):
        # need highest date of completed procedure result
        date_time = MeasurementResult.objects.filter(step_result__procedure_result__work_order=obj).aggregate(Max('date_time'))
        if date_time:
            return date_time["date_time__max"]
        else:
            return None

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'url',
            'name',
            'description',
            'project',
            'start_datetime',
            'last_action_datetime',
            'disposition',
            'disposition_name',
            'test_sequence_definitions',
        ]
