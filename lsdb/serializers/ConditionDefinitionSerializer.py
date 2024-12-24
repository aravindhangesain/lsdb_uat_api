from rest_framework import serializers
from lsdb.models import ConditionDefinition

class ConditionDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ConditionDefinition
        fields = [
            'id',
            'url',
            'name',
            'step_definition',
        ]
