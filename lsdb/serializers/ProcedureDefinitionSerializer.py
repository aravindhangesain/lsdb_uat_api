from rest_framework import serializers
from lsdb.models import ProcedureDefinition
from lsdb.models import StepExecutionOrder

from lsdb.serializers.StepDefinitionSerializer import StepDefinitionSerializer

class StepExecuionOrderSerializer(serializers.ModelSerializer):
    step_definition = StepDefinitionSerializer(many=False)

    class Meta:
        model = StepExecutionOrder
        fields =[
            'execution_group_number',
            'execution_group_name',
            'allow_skip',
            'step_definition',
        ]

class ProcedureDefinitionSerializer(serializers.ModelSerializer):
    step_definitions = StepExecuionOrderSerializer(source = 'stepexecutionorder_set',
        many=True, read_only=True)
    visualizer_name = serializers.ReadOnlyField(source = 'visualizer.name')


    class Meta:
        model = ProcedureDefinition
        fields = [
            'id',
            'url',
            'name',
            'description',
            'work_in_progress_must_comply',
            'group',
            'supersede',
            'disposition',
            'version',
            'unit_type_family',
            'asset_types',
            'linear_execution_group',
            'visualizer',
            'visualizer_name',
            'project_weight',
            'aggregate_duration',
            'step_definitions',
        ]
