from rest_framework import serializers
from lsdb.models import ActionCompletionDefinition

# ProcedureDefinitionSerializer...
class ActionCompletionDefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActionCompletionDefinition
        fields = [
            'id',
            'url',
            'name',
            'plugin_name',
            'plugin_params',
            'expected_result',
        ]
