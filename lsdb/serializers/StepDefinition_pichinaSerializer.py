from rest_framework import serializers
from lsdb.models import StepDefinition_pichina

class StepDefinition_pichinaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StepDefinition_pichina
        fields = [
            'id',
            'url',
            'name',
            'linear_execution_group',
            'step_type',
            # 'measurementdefinition_set',
        ]
