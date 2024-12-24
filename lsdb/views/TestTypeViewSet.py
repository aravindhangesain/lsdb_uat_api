import json
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from lsdb.models import WorkOrder, Unit, TestSequenceDefinition
from lsdb.serializers import TestTypeSerializer

class TestTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = WorkOrder.objects.all()
    serializer_class = TestTypeSerializer

    @action(detail=False, methods=['get'], url_path='find_workorder_and_assign_units')
    def find_workorder_and_assign_units(self, request):
        project_id = request.query_params.get('project_id')
        name = request.query_params.get('name')
        if not project_id or not name:
            return Response({"error": "project_id and name are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            work_order = WorkOrder.objects.get(project_id=project_id, name=name)
            workorder_id = work_order.id
            # Redirect to the assign_units action with the workorder_id
            return self.assign_units(request, pk=workorder_id)
        except WorkOrder.DoesNotExist:
            return Response({"error": "Work order not found"}, status=status.HTTP_404_NOT_FOUND)
        
    @transaction.atomic
    @action(detail=True, methods=['get', 'post'])
    def assign_units(self, request, pk=None):
        self.context = {'request': request}
        try:
            work_order = WorkOrder.objects.get(id=pk)
        except WorkOrder.DoesNotExist:
            return Response({"error": "Work order not found"}, status=status.HTTP_404_NOT_FOUND)
        units = work_order.units.all()
        available_sequences = []
        errors = []
        if request.method == "POST":
            params = json.loads(request.body)
            for test_unit in params:
                try:
                    unit = Unit.objects.get(id=test_unit.get('unit'))
                    test_sequence = TestSequenceDefinition.objects.get(id=test_unit.get('test_sequence'))
                    units_required = work_order.testsequenceexecutiondata_set.filter(
                        test_sequence=test_sequence).first().units_required
                    assigned = units.filter(
                        procedureresult__test_sequence_definition__id=test_sequence.id).distinct().count()
                    if assigned >= units_required:
                        errors.append({
                            'error': f"Unit {unit.serial_number} not assigned to {test_sequence.name}. "
                                    f"{assigned} units already allocated."
                        })
                        continue
                    self.build_bucket(work_order, test_sequence, unit)
                except Unit.DoesNotExist:
                    errors.append({'error': f"Unit with ID {test_unit.get('unit')} does not exist."})
                except TestSequenceDefinition.DoesNotExist:
                    errors.append({'error': f"Test sequence with ID {test_unit.get('test_sequence')} does not exist."})
                except Exception as e:
                    errors.append({'error': str(e)})
            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"status": "Units assigned successfully."}, status=status.HTTP_200_OK)
        # GET request
        response_data = []
        for sequence in work_order.testsequenceexecutiondata_set.all():
            assigned = units.filter(
                procedureresult__test_sequence_definition__id=sequence.test_sequence.id).distinct().count()
            if assigned < sequence.units_required:
                available_sequence_count = sequence.units_required - assigned
                for _ in range(available_sequence_count):
                    response_data.append({
                        "test_sequence_id": sequence.test_sequence.id,
                        "test_sequence_name": sequence.test_sequence.name,
                        "assigned": assigned,
                        "units_required": sequence.units_required,
                        "available_sequence": available_sequence_count
                    })
        return Response(response_data, status=status.HTTP_200_OK)
