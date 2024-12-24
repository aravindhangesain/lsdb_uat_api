from rest_framework import serializers
from lsdb.models import MeasurementResult_pichina, Unit_pichina
from django.utils import timezone
from lsdb.utils.HasHistory_pichina import unit_completion, unit_revenue




class TestSequenceAssignment_pichinaSerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()
    fixture_location_name = serializers.SerializerMethodField()
    unit_type_name = serializers.ReadOnlyField(source='unit_type.name')
    assigned_test_sequence_name = serializers.SerializerMethodField()
    percent_complete =serializers.SerializerMethodField()
    project_weight =serializers.SerializerMethodField()
    last_action_date =serializers.SerializerMethodField()
    execution_group_name = serializers.SerializerMethodField()
    last_action_days =serializers.SerializerMethodField()
    disposition_name = serializers.ReadOnlyField(source='disposition.name') 
    
    def get_percent_complete(self, obj):
        return(unit_completion(obj))
        # measurements = MeasurementResult.objects.filter(step_result__procedure_result__unit=obj).distinct()
        # if measurements.count():
        #     return 100 * (measurements.filter(disposition__isnull=False).count() / measurements.count())
        # else:
        #     return 0

    def get_project_weight(self, obj):
        return(unit_revenue(obj))

    def get_last_action_date(self, obj):
        # this might be an opportunity to store this in the meta
        measurements = MeasurementResult_pichina.objects.filter(step_result__procedure_result__unit=obj,
        date_time__isnull=False).distinct()
        # print(measurements.count())
        if measurements.count():
            return measurements.order_by('date_time').last().date_time
        else:
            return None

    def get_last_action_days(self, obj):
        # this might be an opportunity to store this in the meta
        measurements = MeasurementResult_pichina.objects.filter(step_result__procedure_result__unit=obj,
        date_time__isnull=False).distinct()
        # print(measurements.count())
        if measurements.count():
            return (timezone.now() - measurements.order_by('date_time').last().date_time).days
        else:
            return None

    def get_execution_group_name(self, obj):
        # this might be an opportunity to store this in the meta
        measurements = MeasurementResult_pichina.objects.filter(step_result__procedure_result__unit=obj,
        date_time__isnull=False).distinct()
        # print(measurements.count())
        if measurements.count():
            return measurements.order_by('date_time').last().step_result.procedure_result.name
        else:
            return None
        
    def get_serial_number(self, obj):
        try:
            return obj.serial_number
        except AttributeError:
            return None

    def get_location_name(self, obj):
        try:
            return obj.location.name
        except:
            return None

    def get_fixture_location_name(self, obj):
        try:
            return obj.fixture_location.name
        except:
            return None

    def get_available_sequences(self, obj):
        sequences = []
        for sequence in obj.workorder_pichina_set.first().testsequenceexecutiondata_set.all():
            sequences.append(
            {
                'id':sequence.test_sequence.id,
                'name':sequence.test_sequence.name,
            })
        return sequences

    def get_assigned_test_sequence_name(self, obj):
        name = None
        if  obj.procedureresult_pichina_set.count():
            try:
                name = obj.procedureresult_pichina_set.last().test_sequence_definition.name
            except Exception as e:
                name = None
        return name

    class Meta:
        model = Unit_pichina
        fields = [
            'id',
            'serial_number',
            'unit_type',
            'unit_type_name',
            'assigned_test_sequence_name',
            'location_name',
            'fixture_location_name',
            'disposition_name',
            'percent_complete',
            'project_weight',
            'last_action_date',
            'last_action_days',
            'execution_group_name',
        ]