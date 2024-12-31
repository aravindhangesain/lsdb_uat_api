from rest_framework import serializers
from lsdb.models import ProcedureResult

class GetProcedureDefinitionListSerializer(serializers.ModelSerializer):
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    
    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'procedure_definition',
            'procedure_definition_name',
        ]