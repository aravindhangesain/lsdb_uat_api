from rest_framework import serializers

from lsdb.models import TestSequenceExecutionData_pichina
from lsdb.serializers import TestSequenceDefinition_pichinaSerializer


class TestSequenceExecutionData_pichinaSerializer(serializers.ModelSerializer):
    test_sequence = TestSequenceDefinition_pichinaSerializer(many=False)

    class Meta:
        model = TestSequenceExecutionData_pichina
        fields = [
            'units_required',
            'test_sequence',
            ]
