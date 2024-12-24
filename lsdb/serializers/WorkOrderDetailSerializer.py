from rest_framework import serializers
from lsdb.models import WorkOrder
from lsdb.serializers import UnitListSerializer
from lsdb.serializers import TestSequenceDefinitionSerializer

class WorkOrderDetailSerializer(serializers.HyperlinkedModelSerializer):
    units = UnitListSerializer(many=True, read_only=True)
    test_sequence_definitions = TestSequenceDefinitionSerializer(many=True, read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name')

    class Meta:
        model = WorkOrder
        depth = 1
        fields = [
            'id',
            'url',
            'name',
            'description',
            'project',
            'start_datetime',
            'disposition',
            'disposition_name',
            'test_sequence_definitions',
            'units',        
        ]
