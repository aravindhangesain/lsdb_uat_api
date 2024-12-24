from rest_framework import serializers
from lsdb.models import ProcedureDefinition_pichina


class ProcedureDefinition_pichinaSerializer(serializers.ModelSerializer):
    visualizer_name = serializers.ReadOnlyField(source = 'visualizer.name')


    class Meta:
        model = ProcedureDefinition_pichina
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
            # 'unit_type_family',
            # 'asset_types',
            'linear_execution_group',
            'visualizer',
            'visualizer_name',
            'project_weight',
            'aggregate_duration',
            # 'step_definitions',
        ]
