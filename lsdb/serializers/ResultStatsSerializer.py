from rest_framework import serializers
from lsdb.models import ProcedureResult
from lsdb.models import MeasurementResult
from lsdb.serializers.StepResultSerializer import StepResultSerializer
from lsdb.serializers.UnitTypeSerializer import UnitTypeSerializer
import pandas as pd


class ResultStatsSerializer(serializers.ModelSerializer):
    procedure_definition_name = serializers.SerializerMethodField()
    procedure_count = serializers.SerializerMethodField()
    workday = serializers.SerializerMethodField()

    def get_procedure_definition_name(self, obj):
        return obj.get('procedure_definition__name')

    def get_procedure_count(self, obj):
        return obj.get('procedure_count')

    def get_workday(self, obj):
        return obj.get('workday')

    class Meta:
        model = ProcedureResult
        fields = [
            'procedure_definition_name',
            'procedure_count',
            'workday',
        ]
