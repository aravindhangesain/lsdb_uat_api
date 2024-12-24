from rest_framework import serializers
from lsdb.models import ProcedureResult
from lsdb.models import ProcedureResult_FinalResult
from lsdb.models import Unit


class ProcedureResultVerificationRecordSerializer(serializers.HyperlinkedModelSerializer):
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    disposition_name = serializers.SerializerMethodField()
    completion_date = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    visualizer_name = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')
    reviewed = serializers.SerializerMethodField()
    characterization_point = serializers.ReadOnlyField(source='name')
    final_result = serializers.SerializerMethodField()

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None
        
    def get_final_result(self, instance):
        try:
            final_result_value = ProcedureResult_FinalResult.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult.DoesNotExist:
            return None 

    def get_reviewed(self, obj):
        # measurementresult__reviewed_by_user__isnull=False).count()
        try:
            return (obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__reviewed_by_user__isnull=False).count() != 0)
        except:
            return False

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

    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'visualizer_name',
            'disposition_name',
            'completion_date',
            'username',
            'procedure_definition_name',
            'reviewed',
            'characterization_point',
            'final_result'
        ]

class ProcedureResultVerificationSerializer(serializers.HyperlinkedModelSerializer):
    # procedure_results = serializers.SerializerMethodField()
    project_number = serializers.SerializerMethodField()
    work_order_name = serializers.SerializerMethodField()
    test_sequence_definition_name = serializers.SerializerMethodField()

    # def to_representation(self, data):
    #     iterable = data.all() if isinstance(data, models.Manager) else data
    #     return {
    #         kwdGroup: super().to_representation(Vocab.objects.filter(kwdGroup=kwdGroup))
    #         for kwdGroup in KeyWordGroup.objects.all()
    #     }

    # KLUGE:
    def get_project_number(self, obj):
        needs_review = obj.procedureresult_set.filter(
            disposition__name__iexact='requires review'
        ).first()
        return (needs_review.work_order.project.number)

    def get_work_order_name(self, obj):
        needs_review = obj.procedureresult_set.filter(
            disposition__name__iexact='requires review'
        ).first()
        return (needs_review.work_order.name)

    def get_test_sequence_definition_name(self, obj):
        needs_review = obj.procedureresult_set.filter(
            disposition__name__iexact='requires review'
        ).first()
        return (needs_review.test_sequence_definition.name)

    # def get_procedure_results(self, obj):
    #     needs_review = obj.procedureresult_set.filter(
    #         disposition__name__iexact='requires review'
    #     ).first()
    #     results = obj.procedureresult_set.filter(
    #         linear_execution_group = needs_review.linear_execution_group,
    #         test_sequence_definition = needs_review.test_sequence_definition,
    #     ).distinct().order_by('linear_execution_group')
    #     serializer = ProcedureResultVerificationRecordSerializer(results, many=True)
    #     return (serializer.data)

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_username(self, obj):
        try:
            return obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().user.username
        except:
            return None

    def get_completion_date(self, obj):
        try:
            date_time = obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().date_time
        except:
            date_time = None
        return date_time

    class Meta:
        model = Unit
        fields = [
            'id',
            'url',
            'project_number',
            'work_order_name',
            'serial_number',
            'test_sequence_definition_name',
            # 'procedure_results',
            ]

class ProcedureWorkLogSerializer(serializers.HyperlinkedModelSerializer):
    serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    disposition_name = serializers.SerializerMethodField()
    completion_date = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    characterization_point = serializers.ReadOnlyField(source='name')
    final_result = serializers.SerializerMethodField()

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None
        
    def get_final_result(self, instance):
        try:
            final_result_value = ProcedureResult_FinalResult.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult.DoesNotExist:
            return None 

    def get_username(self, obj):
        try:
            return obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().user.username
        except:
            return None

    def get_completion_date(self, obj):
        try:
            date_time = obj.stepresult_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_set.first().date_time
        except:
            date_time = None
        return date_time

    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'project_number',
            'work_order_name',
            'serial_number',
            'unit',
            'test_sequence_definition_name',
            'procedure_definition_name',
            'disposition_name',
            'completion_date',
            'username',
            'characterization_point',
            'final_result',

            # 'procedure_definition',
            # 'disposition',
            # 'start_datetime',
            # 'end_datetime',
            # 'customer_name',
            # 'work_order',
            # 'linear_execution_group',
            # 'name',
            # 'work_in_progress_must_comply',
            # 'group',
            # 'supersede',
            # 'version',
            # 'test_sequence_definition',
            # 'allow_skip',
        ]
