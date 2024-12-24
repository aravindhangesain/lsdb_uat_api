from rest_framework import serializers
from lsdb.models import ProcedureResult, StepResult, Unit



class verifySerializer(serializers.ModelSerializer):

    unit_id=serializers.ReadOnlyField(source='unit.id')
    visualizer_name = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')
    disposition_name = serializers.SerializerMethodField()
    completion_date = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    reviewed = serializers.SerializerMethodField()
    characterization_point = serializers.ReadOnlyField(source='name')
    # procedure_results=serializers.SerializerMethodField()


    def get_disposition_name(self, obj):
        step_result = StepResult.objects.filter(procedure_result_id=obj.id, disposition__isnull=False).first()
        return step_result.disposition.name if step_result else None
    

    def get_completion_date(self, obj):
        try:
            step_result = StepResult.objects.filter(
                procedure_result_id=obj.id,
                archived=False,
                disposition__isnull=False,
                measurementresult__date_time__isnull=False
            ).first()
            return step_result.measurementresult_set.first().date_time if step_result else None
        except AttributeError:
            return None

    def get_username(self, obj):
        try:
            step_result = StepResult.objects.filter(
                procedure_result_id=obj.id,
                archived=False,
                disposition_id=13
            ).first()
            return step_result.measurementresult_set.first().user.username if step_result else None
        except AttributeError:
            return None

    def get_reviewed(self, obj):
        return StepResult.objects.filter(
            procedure_result_id=obj.id,
            archived=False,
            disposition__isnull=False,
            measurementresult__reviewed_by_user__isnull=False
        ).exists()
    

    
    class Meta:
        model = ProcedureResult
        fields = [
            'unit_id',
            'id',
            'visualizer_name',
            'disposition_name',
            'completion_date',
            'username',
            'procedure_definition_name',
            'reviewed',
            'characterization_point',
            ]