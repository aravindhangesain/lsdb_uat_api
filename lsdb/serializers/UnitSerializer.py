import json
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from django.db import IntegrityError, transaction
from django.db.models import Q, Max, Count,Subquery, OuterRef

from lsdb.models import ProcedureResult
from lsdb.models import ExpectedUnitType
from lsdb.models import Unit
from lsdb.models import AzureFile
from lsdb.models import ProcedureResult_FinalResult

from lsdb.serializers import AzureFileSerializer
from lsdb.serializers import NoteSerializer
from lsdb.serializers import ProjectSerializer
from lsdb.serializers import ProcedureResultSerializer
from lsdb.serializers.UnitTypeSerializer import UnitTypeSerializer


from lsdb.utils.NoteUtils import get_note_counts
from lsdb.utils.HasHistory import unit_history

class UnitTravelerResultSerializer(serializers.ModelSerializer):
### DEPRECATED
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    username = serializers.SerializerMethodField()
    disposition_name = serializers.SerializerMethodField()
    completion_date = serializers.SerializerMethodField()
    reviewed_by_user = serializers.SerializerMethodField()
    review_datetime = serializers.SerializerMethodField()
    visualizer = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_username(self, obj):
        try:
            username = obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().user.username
        except:
            username=None
        return username

    def get_completion_date(self, obj):
        try:
            date_time = obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().date_time
        except:
            date_time = None
        return date_time

    def get_review_datetime(self, obj):
        try:
            date_time = obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().review_datetime
        except:
            date_time = None
        return date_time

    def get_reviewed_by_user(self, obj):
        try:
            username = obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().user.username
        except:
            username = None
        return username

    class Meta:
        data_record = None
        model = ProcedureResult
        fields = [
            'id',
            'procedure_definition',
            'procedure_definition_name',
            'disposition_name',
            'completion_date',
            'username',
            'intake_date',
            'reviewed_by_user',
            'review_datetime',
            'visualizer',
        ]

class UnitGroupedTravelerSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    project_manager = serializers.SerializerMethodField()
    project_number = serializers.SerializerMethodField()
    sequences_results = serializers.SerializerMethodField()
    calibration_results = serializers.SerializerMethodField()
    location = serializers.ReadOnlyField(source='location.name')
    unit_type = UnitTypeSerializer(read_only=True, many=False)
    work_order_name = serializers.SerializerMethodField()
    start_datetime = serializers.SerializerMethodField()
    test_sequence_definition_name = serializers.SerializerMethodField()
    test_sequence_definition_version = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    unit_images = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)

    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)

    @transaction.atomic
    def fill_meta(self, obj):
        try:
            self.Meta.data_record = obj.procedureresult_set.filter(linear_execution_group__gte=1).first()
        except:
            self.Meta.data_record = 1

    @transaction.atomic
    def get_customer_name(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_set.filter(linear_execution_group__gte=1).first().work_order.project.customer.name
        except:
            name=None
        return name

    @transaction.atomic
    def get_test_sequence_definition_name(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_set.filter(linear_execution_group__gte=1).first().test_sequence_definition.name
        except:
            name=None
        return name

    @transaction.atomic
    def get_test_sequence_definition_version(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            version = obj.procedureresult_set.filter(linear_execution_group__gte=1).first().test_sequence_definition.version
        except:
            version=None
        return version

    @transaction.atomic
    def get_work_order_name(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_set.filter(linear_execution_group__gte=1).first().work_order.name
        except:
            name=None
        return name

    @transaction.atomic
    def get_start_datetime(self,obj):
        try:
            start_datetime = obj.workorder_set.first().start_datetime
        except:
            start_datetime = None
        return start_datetime


    @transaction.atomic
    def get_project_manager(self,obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_set.filter(linear_execution_group__gte=1).first().work_order.project.project_manager.username
        except:
            name=None
        return name

    @transaction.atomic
    def get_project_number(self,obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name =obj.procedureresult_set.filter(linear_execution_group__gte=1).first().work_order.project.number
        except:
            name=None
        return name

    def get_calibration_results(self,obj):
        return self.get_grouped_results(obj, ["Calibration"])

    def get_sequences_results(self,obj):
        return self.get_grouped_results(obj, ["Sequences","Control"])

    @transaction.atomic
    def get_grouped_results(self, obj, group):
        # # Subquery to fetch the final_result from ProcedureResultFinalResult
        final_result_subquery = ProcedureResult_FinalResult.objects.filter(
            procedure_result_id=OuterRef('pk')
        ).values('final_result')[:1]

        # Updating the queryset to include final_result using the Subquery
        queryset = obj.procedureresult_set.filter(test_sequence_definition__group__name__in = group)
        queryset = queryset.annotate(
            final_result=Subquery(final_result_subquery),
            completion_date = Max('stepresult__measurementresult__date_time'),
            username = Max('stepresult__measurementresult__user__username'),
            reviewed_by_user = Max('stepresult__measurementresult__reviewed_by_user__username'),
            review_datetime = Max('stepresult__measurementresult__review_datetime'),
            exit_user = Max('stepresult__measurementresult__user__username', filter=Q(stepresult__name="Test End")),
            has_notes = Count('notes', distinct=True),
            open_notes = Count('notes', distinct=True, filter=Q(notes__disposition__complete=False)|Q(notes__disposition__isnull=True)),
            ).order_by('procedure_definition__name') # TODO: issue 1378 right here
            # ).order_by('completion_date') # TODO: issue 1378 right here
        # short circuit empty result set
        if not queryset: return []
        master_data_frame = pd.DataFrame(list(queryset.values(
            'id',
            'name',
            'linear_execution_group',
            'procedure_definition',
            'procedure_definition__name',
            'disposition__name',
            'completion_date',
            'username',
            'reviewed_by_user',
            'review_datetime',
            'procedure_definition__visualizer__name',
            'start_datetime',
            'end_datetime',
            'procedure_definition__aggregate_duration',
            'exit_user',
            'has_notes',
            'test_sequence_definition__hex_color',
            'open_notes',
            'final_result'
        )))
        # master_data_frame.fillna(None)
        # master_data_frame.dropna(inplace=True)
        # master_data_frame.astype({'username':'string'},copy=False)
        # master_data_frame.completion_date.replace({pd.NaT:None})
        filtered = master_data_frame[[
            'id',
            'name',
            'linear_execution_group',
            'procedure_definition',
            'procedure_definition__name',
            'disposition__name',
            'completion_date',
            'username',
            'reviewed_by_user',
            'review_datetime',
            'procedure_definition__visualizer__name',
            'start_datetime',
            'end_datetime',
            'procedure_definition__aggregate_duration',
            'exit_user',
            'has_notes',
            'test_sequence_definition__hex_color',
            'open_notes',
            'final_result'
            ]]
        filtered.columns=[
            'id',
            'name',
            'linear_execution_group',
            'procedure_definition',
            'procedure_definition_name',
            'disposition_name',
            'completion_date',
            'username',
            'reviewed_by_user',
            'review_datetime',
            'visualizer',
            'start_datetime',
            'end_datetime',
            'duration',
            'exit_user',
            'has_notes',
            'tsd_color',
            'open_notes',
            'final_result'
            ]
        # filtered.completion_date.astype(object).where(filtered.completion_date.notna(),None, inplace=True,)
        grouped = filtered.groupby('linear_execution_group')
        results = []
        for name, group in grouped:
            full = {}
            full["procedure_results"] = group.to_dict(orient='records')
            full["name"] = full["procedure_results"][0]["name"]
            full["linear_execution_group"] = full["procedure_results"][0]["linear_execution_group"]
            for result in full["procedure_results"]:
                result['open_notes'] = bool(result["open_notes"])
                result['has_notes'] = bool(result["has_notes"])
                for date_string in ['completion_date','review_datetime','start_datetime','end_datetime']:
                    if str(result[date_string]) == "NaT":
                        result[date_string] = None
            results.append(full)

        return results

    class Meta:
        model = Unit
        data_record = None
        fields = [
            'project_manager',
            'project_number',
            'customer_name',
            'id',
            'url',
            'tib',
            'disposition',
            'disposition_name',
            'test_sequence_definition_name',
            'test_sequence_definition_version',
            'work_order_name',
            'start_datetime',
            'fixture_location',
            'crate',
            'intake_date',
            'serial_number',
            'location',
            'name',
            'description',
            'notes',
            'unit_images',
            'unit_type',
            'calibration_results',
            'sequences_results',
        ]

class UnitGroupedAssetTypeSerializer(serializers.ModelSerializer):
    ### This is not called anywhere any more. It's broken and only here for reference -- MD
    # This is not nearly designed enough. (never was)
    customer_name = serializers.SerializerMethodField()
    project_number = serializers.SerializerMethodField() # Note that get_project_number doesn't exist. Also broken/
    grouped_Units = serializers.SerializerMethodField() # <-- this breaks if you call this code
    location = serializers.ReadOnlyField(source='location.name')
    unit_type = UnitTypeSerializer(read_only=True, many=False)
    work_order_name  = serializers.SerializerMethodField()
    test_sequence_definition_name = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)

    def get_customer_name(self, obj):
        try:
            name = obj.procedureresult_set.first().work_order.project.customer.name
        except:
            name=None
        return name

    def get_grouped_results(self, obj):
        groups = obj.procedureresult_set.values('name', 'linear_execution_group').distinct()
        for group in groups:
            results = obj.procedureresult_set.filter(
                name=group['name'],
                linear_execution_group=group['linear_execution_group']
            ).order_by('procedure_definition__name')
            serializer = UnitTravelerResultSerializer(results, many=True)
            group['procedure_results']=serializer.data

        return (groups)

    class Meta:
        model = Unit
        fields = [
            'project_manager',
            'project_number',
            'customer_name',
            'id',
            'url',
            'test_sequence_definition_name',
            'work_order_name',
            'fixture_location',
            'crate',
            'serial_number',
            'location',
            'name',
            'description',
            'disposition',
            'tib',
            'notes',
            'unit_type',
            'grouped_results',
        ]


class UnitTravelerSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    project_manager = serializers.SerializerMethodField()
    procedure_results = ProcedureResultSerializer(read_only=True, source='procedureresult_set', many=True)
    location = serializers.ReadOnlyField(source='location.name')
    unit_type = UnitTypeSerializer(read_only=True, many=False)
    notes = serializers.SerializerMethodField()

    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)

    def get_customer_name(self, obj):
        try:
            name = obj.procedureresult_set.first().work_order.project.customer.name
        except:
            name=None
        return name

    def get_project_manager(self,obj):
        try:
            name = obj.procedureresult_set.first().work_order.project.project_manager.username
        except:
            name=None
        return name

    class Meta:
        model = Unit
        fields = [
            'project_manager',
            'customer_name',
            'id',
            'url',
            'fixture_location',
            'crate',
            'serial_number',
            'location',
            'name',
            'description',
            'notes',
            'unit_type',
            'procedure_results',
            'disposition',
            'tib',
        ]

class UnitDumpSerializer(serializers.ModelSerializer):
    row = serializers.SerializerMethodField()

    def get_row(self, obj):
        return '{},"{}","{}","{}"'.format(
            obj.id,
            obj.serial_number,
            obj.unit_type.manufacturer.name,
            obj.unit_type.model
            )

    class Meta:
        model = Unit
        fields = ['row',]

class UnitSerializer(serializers.HyperlinkedModelSerializer):
    unit_images = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    history = serializers.SerializerMethodField()
    model = serializers.ReadOnlyField(source='unit_type.model')
    bom = serializers.ReadOnlyField(source='unit_type.bom')
    disposition_name  = serializers.ReadOnlyField(source='disposition.name')
    # work_order = serializers.ReadOnlyField(source='workorder_set[0]')
    notes = serializers.SerializerMethodField()

    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)

    def get_history(self, obj):
        return (unit_history(obj))

    def create(self, validated_data):
        # Need to check if this is an expected_unit_type for a project
        project_set = validated_data.pop('project_set')
        unit_type = validated_data.get('unit_type')
        unit = Unit.objects.create(**validated_data)
        for project in project_set:
            try:
                expected_record = ExpectedUnitType.objects.get(unit_type=unit_type, project=project)
            except ObjectDoesNotExist:
                # silently move along. Nothing to do
                continue
            unit.project_set.add(project)
            unit.save()
            if expected_record:
                expected_record.received_count += 1
                expected_record.save()
        return unit


    class Meta:
        model = Unit
        fields = [
            'id',
            'url',
            'unit_type',
            'fixture_location',
            'crate',
            'intake_date',
            'serial_number',
            'disposition',
            'disposition_name',
            'tib',
            'location',
            'name',
            'model',
            'bom',
            'description',
            'notes',
            'history',
            'project_set',
            'unit_images',
            'workorder_set',
        ]
        read_only_fields =[
            'workorder_set',
            # 'project_set',
            #'unit_images',
        ]
