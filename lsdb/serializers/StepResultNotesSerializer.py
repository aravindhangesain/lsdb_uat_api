from rest_framework import serializers
from lsdb.models import StepResultNotes

class StepResultNotesSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField()
    step_result_name = serializers.ReadOnlyField(source='step_result.name')

    class Meta:
        model = StepResultNotes
        fields = [
            'id',
            'step_result',
            'notes',
            'username',
            'step_result_name',
            'datetime',
            'asset_id',
            'asset_name'
        ]