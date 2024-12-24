import pandas as pd
from rest_framework import serializers
from django.db import transaction
from django.db.models import Q, Max,Subquery, OuterRef
from lsdb.models import Unit_pichina
from lsdb.models import ProcedureResult_FinalResult_pichina
from lsdb.serializers.UnitType_pichinaSerializer import UnitType_pichinaSerializer

class UnitGroupedTraveler_pichinaSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    project_manager = serializers.SerializerMethodField()
    project_number = serializers.SerializerMethodField()
    sequences_results = serializers.SerializerMethodField()
    calibration_results = serializers.SerializerMethodField()
    location = serializers.ReadOnlyField(source='location.name')
    unit_type = UnitType_pichinaSerializer(read_only=True)
    work_order_name = serializers.SerializerMethodField()
    start_datetime = serializers.SerializerMethodField()
    test_sequence_definition_name = serializers.SerializerMethodField()
    test_sequence_definition_version = serializers.SerializerMethodField()
    # notes = serializers.SerializerMethodField()
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    # unit_images = AzureFileSerializer(AzureFile_pichina.objects.all(), many=True, read_only=True)
    

    # def get_notes(self, obj):
    #     user = self.context.get('request').user
    #     return get_note_counts(user,obj)

    @transaction.atomic
    def fill_meta(self, obj):
        try:
            self.Meta.data_record = obj.procedureresult_pichina_set.filter(linear_execution_group__gte=1).first()
        except:
            self.Meta.data_record = 1

    @transaction.atomic
    def get_customer_name(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_pichina_set.filter(linear_execution_group__gte=1).first().work_order.project.customer.name
        except:
            name=None
        return name

    @transaction.atomic
    def get_test_sequence_definition_name(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_pichina_set.filter(linear_execution_group__gte=1).first().test_sequence_definition.name
        except:
            name=None
        return name

    @transaction.atomic
    def get_test_sequence_definition_version(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            version = obj.procedureresult_pichina_set.filter(linear_execution_group__gte=1).first().test_sequence_definition.version
        except:
            version=None
        return version

    @transaction.atomic
    def get_work_order_name(self, obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_pichina_set.filter(linear_execution_group__gte=1).first().work_order.name
        except:
            name=None
        return name

    @transaction.atomic
    def get_start_datetime(self,obj):
        try:
            start_datetime = obj.workorder_pichina_set.first().start_datetime
        except:
            start_datetime = None
        return start_datetime


    @transaction.atomic
    def get_project_manager(self,obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name = obj.procedureresult_pichina_set.filter(linear_execution_group__gte=1).first().work_order.project.project_manager.username
        except:
            name=None
        return name

    @transaction.atomic
    def get_project_number(self,obj):
        if not self.Meta.data_record:
            self.fill_meta(obj)
        try:
            name =obj.procedureresult_pichina_set.filter(linear_execution_group__gte=1).first().work_order.project.number
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
        final_result_subquery = ProcedureResult_FinalResult_pichina.objects.filter(
            procedure_result_id=OuterRef('pk')
        ).values('final_result')[:1]

        # Updating the queryset to include final_result using the Subquery
        queryset = obj.procedureresult_pichina_set.filter(test_sequence_definition__group__name__in = group)
        queryset = queryset.annotate(
            final_result=Subquery(final_result_subquery),
            completion_date = Max('stepresult_pichina__measurementresult_pichina__date_time'),
            username = Max('stepresult_pichina__measurementresult_pichina__user__username'),
            reviewed_by_user = Max('stepresult_pichina__measurementresult_pichina__reviewed_by_user__username'),
            review_datetime = Max('stepresult_pichina__measurementresult_pichina__review_datetime'),
            exit_user = Max('stepresult_pichina__measurementresult_pichina__user__username', filter=Q(stepresult_pichina__name="Test End")),
            # has_notes = Count('notes_pichina', distinct=True),
            # open_notes = Count('notes_pichina', distinct=True, filter=Q(notes__disposition__complete=False)|Q(notes__disposition__isnull=True)),
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
            # 'has_notes',
            'test_sequence_definition__hex_color',
            # 'open_notes',
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
            # 'has_notes',
            'test_sequence_definition__hex_color',
            # 'open_notes',
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
            # 'has_notes',
            'tsd_color',
            # 'open_notes',
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
                # result['open_notes'] = bool(result["open_notes"])
                # result['has_notes'] = bool(result["has_notes"])
                for date_string in ['completion_date','review_datetime','start_datetime','end_datetime']:
                    if str(result[date_string]) == "NaT":
                        result[date_string] = None
            results.append(full)

        return results

    class Meta:
        model = Unit_pichina
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
            # 'crate',
            'intake_date',
            'serial_number',
            'location',
            'name',
            'description',
            # 'notes',
            # 'unit_images',
            'unit_type',
            'calibration_results',
            'sequences_results',
        ]

