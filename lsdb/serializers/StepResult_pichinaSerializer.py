from rest_framework import serializers
from lsdb.models import StepResult_pichina
from lsdb.serializers.MeasurementResult_pichinaSerializer import MeasurementResult_pichinaSerializer

class StepResult_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    measurement_results = MeasurementResult_pichinaSerializer(source='measurementresult_pichina_set', many=True, read_only=True)
    step_definition_id = serializers.ReadOnlyField(source='step_definition.id')
    dates = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        users=[]
        for measurement in obj.measurementresult_pichina_set.all():
            if measurement.user:
                users.append(measurement.user.username)
        return users
    def get_dates(self, obj):
        dates=[]
        for measurement in obj.measurementresult_pichina_set.all():
            if measurement.date_time:
                dates.append(measurement.date_time)
        return dates

    class Meta:
        model = StepResult_pichina
        fields = [
            'id',
            'url',
            'name',
            'notes',
            'procedure_result',
            'step_definition',
            'step_definition_id',
            'execution_number',
            'disposition',
            # 'disposition_codes',
            'start_datetime',
            'duration',
            # 'test_step_result',
            'archived',
            'description',
            'step_number',
            'step_type',
            'linear_execution_group',
            'allow_skip',
            'users',
            'dates',
            'measurement_results',
        ]
