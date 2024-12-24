from rest_framework import serializers

from lsdb.models import Workorder_pichina
from lsdb.serializers.TestSequenceExecutionData_pichinaSerializer import TestSequenceExecutionData_pichinaSerializer



class Workorder_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    test_sequence_definitions = TestSequenceExecutionData_pichinaSerializer(source='testsequenceexecutiondata_pichina_set',
        many=True, read_only=True
        )
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    project_number = serializers.ReadOnlyField(source='project.number')
    unit_disposition_name = serializers.ReadOnlyField(source='unit_disposition.name')

    class Meta:
        model = Workorder_pichina
        fields = [
            'id',
            'url',
            'name',
            'description',
            'project',
            'project_number',
            'start_datetime', # NTP Date
            'disposition',
            'disposition_name',
            'unit_disposition',
            'unit_disposition_name',
            'tib',
            'test_sequence_definitions',
        ]