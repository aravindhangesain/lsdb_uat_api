
from rest_framework import serializers
from django.db.models import Q
from lsdb.models import ProcedureResult_pichina
from lsdb.models import ProcedureResult_FinalResult_pichina
from lsdb.serializers.StepResult_pichinaSerializer import StepResult_pichinaSerializer




class Procedureresult_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    step_results = StepResult_pichinaSerializer(source='stepresult_pichina_set', many=True, read_only=True)
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    disposition_name = serializers.SerializerMethodField()
    visualizer = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')
    # assets = serializers.SerializerMethodField()
    # has_notes = serializers.SerializerMethodField()
    # open_notes = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()

    
    def get_final_result(self, instance):
        try:
            final_result_value = ProcedureResult_FinalResult_pichina.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult_pichina.DoesNotExist:
            return None

   

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None



    class Meta:
        model = ProcedureResult_pichina
        fields = [
            'id',
            'url',
            'unit',
            'procedure_definition',
            'procedure_definition_name',
            'disposition',
            'disposition_name',
            'start_datetime',
            'end_datetime',
            'customer_name',
            'project_number',
            'work_order',
            'work_order_name',
            'linear_execution_group',
            'name',
            'work_in_progress_must_comply',
            # 'group',
            'supersede',
            'version',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'allow_skip',
            'step_results',
            'visualizer',
            # 'assets',
            # 'has_notes',
            # 'open_notes',
            'final_result'
        ]



  