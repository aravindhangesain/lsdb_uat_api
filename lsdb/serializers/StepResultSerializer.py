from rest_framework import serializers
from lsdb.models import StepResult
from lsdb.serializers.MeasurementResultSerializer import MeasurementResultSerializer
from lsdb.serializers.MeasurementResultSerializer import MeasurementResultStressSerializer

class StepResultSerializer(serializers.HyperlinkedModelSerializer):
    measurement_results = MeasurementResultSerializer(source='measurementresult_set', many=True, read_only=True)
    step_definition_id = serializers.ReadOnlyField(source='step_definition.id')
    dates = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        users=[]
        for measurement in obj.measurementresult_set.all():
            if measurement.user:
                users.append(measurement.user.username)
        return users
    def get_dates(self, obj):
        dates=[]
        for measurement in obj.measurementresult_set.all():
            if measurement.date_time:
                dates.append(measurement.date_time)
        return dates
        # source='measurementresult_set.user.name' , many=True, read_only=True)

    class Meta:
        model = StepResult
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
            'test_step_result',
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

class StepResultStressSerializer(serializers.HyperlinkedModelSerializer):
    measurement_results = MeasurementResultStressSerializer(source='measurementresult_set', many=True, read_only=True)
    step_definition_id = serializers.ReadOnlyField(source='step_definition.id')
    dates = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()

    def get_users(self, obj):
        users=[]
        for measurement in obj.measurementresult_set.all():
            if measurement.user:
                users.append(measurement.user.username)
        return users
    def get_dates(self, obj):
        dates=[]
        for measurement in obj.measurementresult_set.all():
            if measurement.date_time:
                dates.append(measurement.date_time)
        return dates
        # source='measurementresult_set.user.name' , many=True, read_only=True)

    class Meta:
        model = StepResult
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
            'test_step_result',
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
