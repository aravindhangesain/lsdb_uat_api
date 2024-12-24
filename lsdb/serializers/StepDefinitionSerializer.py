from rest_framework import serializers
from lsdb.models import StepDefinition

class StepDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StepDefinition
        fields = [
            'id',
            'url',
            'name',
            'linear_execution_group',
            'step_type',
            'measurementdefinition_set',
        ]
