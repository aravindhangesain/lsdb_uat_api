from rest_framework import serializers
from lsdb.models import ProcedureResult

class GetTestSequenceDefinitionListSerializer(serializers.ModelSerializer):
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    
    class Meta:
        model = ProcedureResult
        fields = [
            'test_sequence_definition',
            'test_sequence_definition_name',
        ]