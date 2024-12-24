from rest_framework import serializers
from lsdb.models import ProcedureResult_FinalResult


class ProcedureResult_FinalResultSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProcedureResult_FinalResult
        fields = [
            'procedure_result',
            'final_result',
            'updated_date',
            'procedure_definition'
        ]