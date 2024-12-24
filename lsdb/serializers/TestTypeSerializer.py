from rest_framework import serializers
from lsdb.models import WorkOrder, TestSequenceExecutionData, TestSequenceDefinition, Unit
class TestTypeSerializer(serializers.ModelSerializer):
    test_sequence_id = serializers.SerializerMethodField()
    test_sequence_name = serializers.SerializerMethodField()
    units_required = serializers.SerializerMethodField()
    assigned_units = serializers.SerializerMethodField()
    available_sequence = serializers.SerializerMethodField()
    def get_test_sequence_id(self, obj):
        test_sequence_executions = TestSequenceExecutionData.objects.filter(work_order_id=obj.id)
        return [execution.test_sequence_id for execution in test_sequence_executions]
    def get_test_sequence_name(self, obj):
        test_sequence_executions = TestSequenceExecutionData.objects.filter(work_order_id=obj.id)
        test_sequence_names = []
        for execution in test_sequence_executions:
            try:
                test_sequence_definition = TestSequenceDefinition.objects.get(id=execution.test_sequence_id)
                test_sequence_names.append(test_sequence_definition.name)
            except TestSequenceDefinition.DoesNotExist:
                continue
        return test_sequence_names
    def get_units_required(self, obj):
        test_sequence_executions = TestSequenceExecutionData.objects.filter(work_order_id=obj.id)
        return [execution.units_required for execution in test_sequence_executions]
    def get_assigned_units(self, obj):
        test_sequence_executions = TestSequenceExecutionData.objects.filter(work_order_id=obj.id)
        assigned_units = []
        for execution in test_sequence_executions:
            assigned_count = Unit.objects.filter(
                procedureresult__test_sequence_definition__id=execution.test_sequence_id).distinct().count()
            assigned_units.append(assigned_count)
        return assigned_units
    def get_available_sequence(self, obj):
        test_sequence_executions = TestSequenceExecutionData.objects.filter(work_order_id=obj.id)
        available_sequences = []
        for execution in test_sequence_executions:
            assigned = Unit.objects.filter(
                procedureresult__test_sequence_definition__id=execution.test_sequence_id).distinct().count()
            available_sequence = execution.units_required - assigned
            available_sequences.append(available_sequence)
        return available_sequences
    class Meta:
        model = WorkOrder
        fields = [
            'test_sequence_name',
            'units_required',
            'test_sequence_id',
            'available_sequence',
            'assigned_units'
        ]