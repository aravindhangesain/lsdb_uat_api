from rest_framework import serializers
from django.db.models import Max
from lsdb.models import MeasurementResult_pichina
from lsdb.models import Workorder_pichina
from lsdb.serializers.TestSequenceDefinition_pichinaSerializer import TestSequenceDefinition_pichinaSerializer

class WorkorderList_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    test_sequence_definitions = TestSequenceDefinition_pichinaSerializer(many=True, read_only=True)
    last_action_datetime = serializers.SerializerMethodField()

    def get_last_action_datetime(self, obj):
        date_time = MeasurementResult_pichina.objects.filter(step_result__procedure_result__work_order=obj).aggregate(Max('date_time'))
        if date_time:
            return date_time["date_time__max"]
        else:
            return None

    class Meta:
        model = Workorder_pichina
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
