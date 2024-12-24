from rest_framework import serializers
from django.db.models import Q, Max
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.db import IntegrityError, transaction

from lsdb.models import WorkOrder
from lsdb.models import Unit
from lsdb.models import MeasurementResult
from lsdb.models import ProcedureResult
from lsdb.models import Project
from lsdb.models import TestSequenceDefinition
from lsdb.models import TestSequenceExecutionData
from lsdb.models import Disposition
from lsdb.models import ExpectedUnitType

from lsdb.serializers.TestSequenceDefinitionSerializer import TestSequenceDefinitionSerializer
from lsdb.utils.HasHistory import work_order_measurements_completed, work_order_measurements_requested, unit_completion, unit_revenue
from lsdb.utils.NoteUtils import get_note_counts
from lsdb.serializers.NoteSerializer import NoteSerializer

class AvailableSequenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestSequenceDefinition
        fields = [
            'id',
            'name',
            ]


class TestSequenceAssignmentSerializer(serializers.ModelSerializer):
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
        measurements = MeasurementResult.objects.filter(step_result__procedure_result__unit=obj,
        date_time__isnull=False).distinct()
        # print(measurements.count())
        if measurements.count():
            return measurements.order_by('date_time').last().date_time
        else:
            return None

    def get_last_action_days(self, obj):
        # this might be an opportunity to store this in the meta
        measurements = MeasurementResult.objects.filter(step_result__procedure_result__unit=obj,
        date_time__isnull=False).distinct()
        # print(measurements.count())
        if measurements.count():
            return (timezone.now() - measurements.order_by('date_time').last().date_time).days
        else:
            return None

    def get_execution_group_name(self, obj):
        # this might be an opportunity to store this in the meta
        measurements = MeasurementResult.objects.filter(step_result__procedure_result__unit=obj,
        date_time__isnull=False).distinct()
        # print(measurements.count())
        if measurements.count():
            return measurements.order_by('date_time').last().step_result.procedure_result.name
        else:
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
        for sequence in obj.workorder_set.first().testsequenceexecutiondata_set.all():
            sequences.append(
            {
                'id':sequence.test_sequence.id,
                'name':sequence.test_sequence.name,
            })
        return sequences

    def get_assigned_test_sequence_name(self, obj):
        name = None
        if  obj.procedureresult_set.count():
            try:
                name = obj.procedureresult_set.last().test_sequence_definition.name
            except Exception as e:
                name = None
        return name

    class Meta:
        model = Unit
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

class TestSequenceExecutionDataSerializer(serializers.ModelSerializer):
    test_sequence = TestSequenceDefinitionSerializer(many=False)

    class Meta:
        model = TestSequenceExecutionData
        fields = [
            'units_required',
            'test_sequence',
            ]

class WorkOrderExpectedUnitTypeSerializer(serializers.HyperlinkedModelSerializer):
    manufacturer = serializers.ReadOnlyField(source='unit_type.manufacturer.name', read_only=True)
    model = serializers.ReadOnlyField(source='unit_type.model', read_only=True)
    bom = serializers.ReadOnlyField(source='unit_type.bom', read_only=True)
    class Meta:
        model = ExpectedUnitType
        fields = [
            'id',
            'url',
            'expected_count',
            'received_count',
            'unit_type',
            'manufacturer',
            'model',
            'bom',
        ]

class WorkOrderIntakeSerializer(serializers.HyperlinkedModelSerializer):
    project_number = serializers.ReadOnlyField(source='project.number')
    project_id = serializers.ReadOnlyField(source='project.id')
    project_manager_name = serializers.ReadOnlyField(source='project.project_manager.username')
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    # expected_unit_types = WorkOrderExpectedUnitTypes(source='project.expectedunittype_set',many=True)
    # project_notes = NoteSerializer(source='project.notes', many=True, read_only=True)
    project_notes = serializers.SerializerMethodField()
    # expected_unit_types = ExpectedUnitTypeSerializer(ExpectedUnitType.objects.project_set.all(), read_only=True)
    # expected_unit_types = serializers.SerializerMethodField()
    #
    # def get_expected_unit_types(self, obj):
    #     return ExpectedUnitTypeSerializer(obj.project_set.all(), many=True, context=self.context).data

    def get_project_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj.project)

    class Meta:
        model = WorkOrder
        fields = [
            'project',
            'project_id',
            'project_number',
            'id',
            'url',
            'name',
            'project_manager_name',
            'start_datetime',
            'disposition',
            'disposition_name',
            'project_notes',
            # 'expected_unit_types',
        ]

class WorkOrderProjectSerializer(serializers.ModelSerializer):
    unit_count = serializers.SerializerMethodField()
    percent_complete = serializers.SerializerMethodField()
    last_action_days = serializers.SerializerMethodField()
    last_action_date = serializers.SerializerMethodField()
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)

    @transaction.atomic
    def fill_meta(self, obj):
        queryset = obj.procedureresult_set.filter(stepresult__measurementresult__disposition__isnull=False)
        queryset = queryset.annotate(last_result = Max('stepresult__measurementresult__date_time'))
        try:
            results, = max(queryset.filter(last_result__isnull=False).values_list('last_result'))
            self.Meta.meta_days = (timezone.now() - results).days
            self.Meta.meta_date = results
        except:
            self.Meta.meta_days = 0
            self.Meta.meta_date = None
        return self.Meta.meta_days, self.Meta.meta_date

    def get_last_action_days(self, obj):
        if self.Meta.meta_days != None:
            return self.Meta.meta_days
        else:
            days, date = self.fill_meta(obj)
            return days

    def get_last_action_date(self, obj):
        if self.Meta.meta_days != None:
            return self.Meta.meta_date
        else:
            days, date = self.fill_meta()
            return date

    def get_unit_count(self, obj):
        return obj.units.count()

    def get_percent_complete(self, obj):
        return work_order_measurements_completed(obj)

    class Meta:
        meta_days = None
        meta_date = timezone.now().date()
        model = WorkOrder
        fields = [
            'id',
            'url',
            'name',
            'disposition_name',
            'percent_complete',
            'unit_count',
            'last_action_days',
            'last_action_date',
        ]

class WorkOrderSerializer(serializers.HyperlinkedModelSerializer):
    test_sequence_definitions = TestSequenceExecutionDataSerializer(source='testsequenceexecutiondata_set',
        many=True, read_only=True
        )
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    project_number = serializers.ReadOnlyField(source='project.number')
    unit_disposition_name = serializers.ReadOnlyField(source='unit_disposition.name')

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'url',
            'name',
            'description',
            'project',
            'project_number',
            'start_datetime', # NTP Date
            'disposition',
            'disposition_name',
            'unit_disposition',
            'unit_disposition_name',
            # 'units', # This makes the world turn slower
            'tib',
            'test_sequence_definitions',
        ]
