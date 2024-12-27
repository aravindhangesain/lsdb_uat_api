from rest_framework import serializers
from lsdb.models import ProcedureResult_FinalResult_pichina, ProcedureResult_pichina


class ProcedureWorkLog_pichinaSerializer(serializers.HyperlinkedModelSerializer):
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
            final_result_value = ProcedureResult_FinalResult_pichina.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult_pichina.DoesNotExist:
            return None 

    def get_username(self, obj):
        try:
            return obj.stepresult_pichina_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_pichina_set.first().user.username
        except:
            return None

    def get_completion_date(self, obj):
        try:
            date_time = obj.stepresult_pichina_set.filter(archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False).first().measurementresult_pichina_set.first().date_time
        except:
            date_time = None
        return date_time

    class Meta:
        model = ProcedureResult_pichina
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