import json
from django.db import transaction
from rest_framework import viewsets


from lsdb.models import MeasurementResult_pichina, TestSequenceDefinition_pichina
from lsdb.models import ProcedureResult_pichina
from lsdb.models import StepResult_pichina
from lsdb.models import Unit_pichina
from lsdb.models import Workorder_pichina
from lsdb.permissions import IsAdminOrSelf
from lsdb.serializers import TestSequenceAssignment_pichinaSerializer
from lsdb.serializers import Workorder_pichinaSerializer
from lsdb.serializers import WorkorderList_pichinaSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class Workorder_pichinaViewSet(viewsets.ModelViewSet):
    queryset = Workorder_pichina.objects.all()
    serializer_class = Workorder_pichinaSerializer

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkorderList_pichinaSerializer,
            permission_classes=[IsAdminOrSelf, ]
            )
    def assign_units(self, request, pk=None):
        self.context = {'request': request}
        work_order = Workorder_pichina.objects.get(id=pk)
        unit_ids = work_order.get_units()
        units = Unit_pichina.objects.filter(id__in=unit_ids)
        available_sequences = []
        errors = []

        if request.method == "POST":
            params = json.loads(request.body)
            for test_unit in params:
                unit = Unit_pichina.objects.get(id=test_unit.get('unit'))
                test_sequence = TestSequenceDefinition_pichina.objects.get(id=test_unit.get('test_sequence'))
                units_required = work_order.testsequenceexecutiondata_pichina_set.filter(
                    test_sequence=test_sequence).first().units_required
                assigned = units.filter(
                    procedureresult_pichina__test_sequence_definition__id=test_sequence.id).distinct().count()
                if assigned >= units_required:
                    errors.append({'error': "unit {} not assigned to {}. {} units already allocated.".format(
                        unit.serial_number, test_sequence.name, assigned
                    )})
                    continue
                self.build_bucket(work_order, test_sequence, unit)
            if len(errors):
                return Response(errors)
        for sequence in work_order.testsequenceexecutiondata_pichina_set.all():
            assigned = units.filter(
                procedureresult_pichina__test_sequence_definition__id=sequence.test_sequence.id).distinct().count()
            if assigned < sequence.units_required:
                available_sequences.append(
                    {
                        'id': sequence.test_sequence.id,
                        'name': sequence.test_sequence.name,
                        'assigned': assigned,
                        'units_required': sequence.units_required,
                        'disposition': sequence.test_sequence.disposition_id,
                        'disposition_name':sequence.test_sequence.disposition.name
                    }
                )
        serializer = TestSequenceAssignment_pichinaSerializer(units, many=True, context=self.context)
        return Response({
            'available_sequences': available_sequences,
            'units': serializer.data})

    @transaction.atomic
    def build_bucket(self, work_order, test_sequence, unit):
        for execution in test_sequence.procedureexecutionorder_set.all():
            if (not execution.execution_condition == None and len(execution.execution_condition)!=0):
                ldict = {'unit': unit, 'retval': False}
                exec('retval={}'.format(execution.execution_condition), None, ldict)
                if ldict['retval'] == False:
                    continue
            procedure_result = ProcedureResult_pichina.objects.create(
                unit=unit,
                name=execution.execution_group_name,
                disposition=None,
                group=execution.procedure_definition.group,
                work_order=work_order,
                procedure_definition=execution.procedure_definition,
                version=execution.procedure_definition.version,
                linear_execution_group=execution.execution_group_number,
                test_sequence_definition=test_sequence,
                allow_skip=execution.allow_skip,
            )
            for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
                step_result = StepResult_pichina.objects.create(
                    name=step_execution.execution_group_name,
                    procedure_result=procedure_result,
                    step_definition=step_execution.step_definition,
                    execution_number=0,
                    disposition=None,
                    start_datetime=None,
                    duration=0,
                    test_step_result=None,
                    archived=False,
                    description=None,
                    step_number=0,
                    step_type=step_execution.step_definition.step_type,
                    linear_execution_group=step_execution.execution_group_number,
                    allow_skip=step_execution.allow_skip,
                )
                for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                    measurement_result = MeasurementResult_pichina.objects.create(
                        step_result=step_result,
                        measurement_definition=measurement_definition,
                        software_revision=0.0,
                        disposition=None,
                        limit=measurement_definition.limit,
                        station=0,
                        name=measurement_definition.name,
                        record_only=measurement_definition.record_only,
                        allow_skip=measurement_definition.allow_skip,
                        requires_review=measurement_definition.requires_review,
                        measurement_type=measurement_definition.measurement_type,
                        order=measurement_definition.order,
                        report_order=measurement_definition.report_order,
                        measurement_result_type=measurement_definition.measurement_result_type,
                    )