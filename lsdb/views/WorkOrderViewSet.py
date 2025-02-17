import datetime
import json
from django.db import IntegrityError, transaction

import requests
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.status import (HTTP_400_BAD_REQUEST)

from lsdb.models import ActionDefinition, Project
from lsdb.models import Disposition
from lsdb.models import DispositionCode
from lsdb.models import WorkOrder
from lsdb.models import Unit
from lsdb.models import MeasurementResult
from lsdb.models import StepResult
from lsdb.models import ProcedureResult
from lsdb.models import TestSequenceDefinition
from lsdb.models import TestSequenceExecutionData
from lsdb.models import ProcedureExecutionOrder,WorkOrderTemplate

from lsdb.serializers import ActionResultSerializer
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.serializers import WorkOrderSerializer
from lsdb.serializers import WorkOrderIntakeSerializer
from lsdb.serializers import WorkOrderExpectedUnitTypeSerializer
from lsdb.serializers import WorkOrderListSerializer
from lsdb.serializers import WorkOrderDetailSerializer
from lsdb.serializers import TestSequenceAssignmentSerializer
from lsdb.permissions import ConfiguredPermission, IsAdminOrSelf
from lsdb.utils.HasHistory import unit_history, project_history
from lsdb.utils.ActionUtils import create_action


class WorkOrderViewSet(
    # DetailSerializerMixin,
    LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows WorkOrder to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    # queryset = WorkOrder.objects.all().prefetch_related('units')
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    # serializer_detail_class = WorkOrderDetailSerializer
    permission_classes = [ConfiguredPermission]

    def perform_create(self, serializer):
        created_workorder = serializer.save()
        largest_id = WorkOrderTemplate.objects.order_by('-id').values_list('id', flat=True).first() or 0
        WorkOrderTemplate.objects.create(
            workorder=created_workorder, 
            template_name=f"Template_{largest_id + 1}-{created_workorder.name}"
        )

                






    @action(detail=False, methods=['get', ],
            serializer_class=DispositionCodeListSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def dispositions(self, request, pk=None):
        self.context = {'request': request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='work_orders'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get', ],
            serializer_class=DispositionCodeListSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def unit_dispositions(self, request, pk=None):
        self.context = {'request': request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='work_order_units'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'],
            permission_classes=(ConfiguredPermission,)
            )
    def intake_units(self, request, pk=None):
        self.context = {'request': request}

        queryset = WorkOrder.objects.all()
        serializer = WorkOrderIntakeSerializer(
            queryset,
            many=True,
            context=self.context
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
            serializer_class=WorkOrderDetailSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def units(self, request, pk=None):
        self.context = {'request': request}
        queryset = WorkOrder.objects.get(id=pk)
        serializer = WorkOrderDetailSerializer(
            queryset,
            many=False,
            context=self.context
        )
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
            serializer_class=WorkOrderExpectedUnitTypeSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def expected_unit_types(self, request, pk=None):
        self.context = {'request': request}

        queryset = WorkOrder.objects.get(id=pk).project.expectedunittype_set.all()
        serializer = WorkOrderExpectedUnitTypeSerializer(
            queryset,
            many=True,
            context=self.context
        )
        return Response(serializer.data)

    # KLUGE. should be temporary
    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderListSerializer,
            permission_classes=[IsAdminOrSelf, ]
            )
    def assign_units(self, request, pk=None):
        """
        this is a dual purpose endpoint. it replies with the test sequences available, or assigned
        for the work order.

        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        units = work_order.units.all()
        available_sequences = []
        errors = []

        if request.method == "POST":
            # do the needful
            params = json.loads(request.body)
            # Copy this code again...
            for test_unit in params:
                # TODO: Wrap this with exception handler
                unit = Unit.objects.get(id=test_unit.get('unit'))
                test_sequence = TestSequenceDefinition.objects.get(id=test_unit.get('test_sequence'))
                # Cowardly do not allow over allocation:
                units_required = work_order.testsequenceexecutiondata_set.filter(
                    test_sequence=test_sequence).first().units_required
                assigned = units.filter(
                    procedureresult__test_sequence_definition__id=test_sequence.id).distinct().count()
                if assigned >= units_required:
                    errors.append({'error': "unit {} not assigned to {}. {} units already allocated.".format(
                        unit.serial_number, test_sequence.name, assigned
                    )})
                    continue
                self.build_bucket(work_order, test_sequence, unit)
            if len(errors):
                return Response(errors)
        # GET:
        for sequence in work_order.testsequenceexecutiondata_set.all():
            # TODO: This count doesn't account for reassignment. Need to set a disposition on the
            # procedure_results when we "end testing"
            assigned = units.filter(
                procedureresult__test_sequence_definition__id=sequence.test_sequence.id).distinct().count()
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
        serializer = TestSequenceAssignmentSerializer(units, many=True, context=self.context)
        return Response({
            'available_sequences': available_sequences,
            'units': serializer.data})

    @transaction.atomic
    def build_bucket(self, work_order, test_sequence, unit):
        for execution in test_sequence.procedureexecutionorder_set.all():
            # Check if I should add this:
            if (not execution.execution_condition == None and len(execution.execution_condition)!=0):
                ldict = {'unit': unit, 'retval': False}
                exec('retval={}'.format(execution.execution_condition), None, ldict)
                # we'll keep adding rear side flashes if we don't know
                if ldict['retval'] == False:
                    continue
            # print(procedure.procedureexecutionorder_set.all()[0])
            procedure_result = ProcedureResult.objects.create(
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
                step_result = StepResult.objects.create(
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
                    measurement_result = MeasurementResult.objects.create(
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

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderListSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def test_units(self, request, pk=None):
        """
        This action endpoint is used to link units to a test sequence in the work order.
        to add units to a work order, POST the following:
        [
            { "unit": 1, "copy_history":true, "test_sequence":1 },
            { "unit": 2, "copy_history":true, "test_sequence":2 }
        ]
        units: unit to attach,
        copy_history: copy any previous project history to this test Sequence
        test_sequence: id of the test sequence in this work order to attach this unit

        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        if request.method == "POST":
            # do the needful
            params = json.loads(request.body)
            for test_unit in params:
                # TODO: Wrap this with exception handler
                # key = test_unit.get('unit')
                unit = Unit.objects.get(id=test_unit.get('unit'))
                test_sequence = TestSequenceDefinition.objects.get(id=test_unit.get('test_sequence'))
                if test_unit.get('copy_history') and unit_history(unit):
                    pass
                    # this isn't right yet:
                    # History is not being copied, old structure persists.
                    # need to find only the data that has been generated
                    # for procedure in test_sequence.procedure_definitions.all():
                    #     # if there is a result for this procedure in the past
                    #     procedure_result = ProcedureResult.objects.create(
                    #         unit = unit,
                    #         name = procedure.name,
                    #         disposition = None,
                    #         group = procedure.group,
                    #         work_order = work_order,
                    #         procedure_definition = procedure,
                    #         version = procedure.version,
                    #         # this should be the execution order copied into here:
                    #         linear_execution_group = procedure.linear_execution_group,
                    #         test_sequence_definition = test_sequence,
                    #         # allow_skip =
                    #     )
                    #     for step_definition in procedure.step_definitions.all():
                    #         step_result = StepResult.objects.create(
                    #             name = step_definition.name,
                    #             procedure_result = procedure_result,
                    #             step_definition = step_definition,
                    #             execution_number = 0,
                    #             disposition = None,
                    #             start_datetime = None,
                    #             duration = 0,
                    #             test_step_result = None,
                    #             archived = False,
                    #             description = None,
                    #             step_number = 0,
                    #             step_type = step_definition.step_type,
                    #             linear_execution_group = step_definition.linear_execution_group,
                    #         )
                    #         for measurement_definition in step_definition.measurementdefinition_set.all():
                    #             measurement_result = MeasurementResult.objects.create(
                    #                 step_result = step_result,
                    #                 measurement_definition = measurement_definition.id,
                    #                 software_revision = 0.0,
                    #                 disposition = None,
                    #                 limit = measurement_definition.limit,
                    #                 station = 0,
                    #                 name = measurement_definition.name,
                    #                 record_only = measurement_definition.record_only,
                    #                 allow_skip = measurement_definition.allow_skip,
                    #                 requires_review = measurement_definition.requires_review,
                    #                 measurement_type = measurement_definition.measurement_type,
                    #                 order = measurement_definition.order,
                    #                 report_order = measurement_definition.report_order,
                    #             )

                else:
                    self.build_bucket(work_order, test_sequence, unit)

        serializer = WorkOrderListSerializer(work_order, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderListSerializer,
            permission_classes=[IsAdminOrSelf, ]
            )
    def kluge_units(self, request, pk=None):
        """
        This action endpoint is used to link units to a test sequence in the work order.
        to add uints to a work order, POST the following:
        [
            { "unit": 1, "test_sequence":1 },
            { "unit": 2, "test_sequence":2 }
        ]
        units: unit to attach,
        copy_history: copy any previous project history to this test Sequence
        test_sequence: id of the test sequence in this work order to attach this unit

[
{ "unit": 1, "test_sequence":5 },
{ "unit": 2, "test_sequence":5 },
{ "unit": 3, "test_sequence":4 },
{ "unit": 4, "test_sequence":4 },
{ "unit": 5, "test_sequence":10 },
{ "unit": 6, "test_sequence":10 },
{ "unit": 7, "test_sequence":8 },
{ "unit": 8, "test_sequence":8 },
{ "unit": 9, "test_sequence":12 },
{ "unit": 10, "test_sequence":12 }
]

        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        if request.method == "POST":
            # do the needful
            params = json.loads(request.body)
            for test_unit in params:
                # TODO: Wrap this with exception handler
                # key = test_unit.get('unit')
                unit = Unit.objects.get(id=test_unit.get('unit'))
                test_sequence = TestSequenceDefinition.objects.get(id=test_unit.get('test_sequence'))
                for execution in test_sequence.procedureexecutionorder_set.all():
                    # print(procedure.procedureexecutionorder_set.all()[0])
                    procedure_result = ProcedureResult.objects.create(
                        unit=unit,
                        name=execution.execution_group_name,
                        disposition=None,
                        group=execution.procedure_definition.group,
                        work_order=work_order,
                        procedure_definition=execution.procedure_definition,
                        version=execution.procedure_definition.version,
                        linear_execution_group=execution.execution_group_number,
                        test_sequence_definition=test_sequence,
                        allow_skip=True,
                    )
                    for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
                        step_result = StepResult.objects.create(
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
                            measurement_result = MeasurementResult.objects.create(
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

        serializer = WorkOrderListSerializer(work_order, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def delete_tests(self, request, pk=None):
        """
        This action is used to remove test sequence definitions from a work order.
        The link is located via perfect matches to test_sequence. This does not delete
        any results that have been created, so it will mess with completion specs.
        POST:
        [
            {
                "test_sequence": 1
            },
            ...
        ]
        "test_sequence": ID of the test sequence to delete

        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for procedure in params:
                test_sequence = TestSequenceDefinition.objects.get(id=procedure.get('test_sequence'))

                TestSequenceExecutionData.objects.filter(
                    work_order=work_order,
                    test_sequence=test_sequence,
                ).delete()

        serializer = WorkOrderSerializer(work_order, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ActionResultSerializer,
            )
    def new_action(self, request, pk=None):
        """
        This endpoint can be used to create a new ActionResult bucket that is not specifically tied
        to a ActionPlanDefinition, but is tied to this work order.
        POST:
        {
                "name":"", Required
                "description":"",
                "disposition":$ID,Required
                "action_definition":$ID,Required
                "execution_group":"", optional
                "done_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "start_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "promise_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "eta_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "groups":[
                    ID(s)
                ]
       }
        """
        self.context = {'request': request}
        if request.method == 'POST':
            params = request.data
            disposition = params.get('disposition')
            if disposition and (type(disposition) == int):
                disposition = Disposition.objects.get(id=disposition)
            groups = params.get('groups')
            parent_object = WorkOrder.objects.get(pk=pk)
            action_definition = ActionDefinition.objects.get(id=params.get('action_definition'))

            action, status = create_action(
                action_definition=action_definition,
                disposition=disposition,
                groups=groups,
                parent_object=parent_object,
                request_params=params,
            )
            if status:
                serializer = ActionResultSerializer(action, many=False, context=self.context)
            else:
                return Response({"error": action.__str__()}, status=HTTP_400_BAD_REQUEST)
        else:  # GET
            serializer = ActionResultSerializer([], many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def add_tests(self, request, pk=None):
        """
        This action is used to add test sequences to a work order. This limits the instances of a test to exactly 1.
        POST:
        [
            {
                "test_sequence": 1,
                "units_required": 4
            },
            ...
        ]
        "test_sequence": test sequence to attach,
        "units_required": number of units to be allocated to this test sequence.
        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for sequence in params:
                test_sequence = TestSequenceDefinition.objects.get(id=sequence.get('test_sequence'))
                # TODO: Better exception handling here
                TestSequenceExecutionData.objects.create(
                    units_required=sequence.get('units_required'),
                    work_order=work_order,
                    test_sequence=test_sequence,
                )
        serializer = WorkOrderSerializer(work_order, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def autoassign_units(self, request, pk=None):
        """
        This action endpoint is used to link units to the work order and
        autoassign to test sequences
        [
            "1","2"
        ]
        where the numbers represent a unit ID to link
        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            params.reverse()
            # work_order.units.filter(procedureresult__test_sequence_definition__id=sequence.test_sequence.id).distinct().count()

            test_sequences = list(work_order.testsequenceexecutiondata_set.filter().values().order_by('test_sequence'))
            test_sequences.reverse()
            errors = []
            while (len(test_sequences)):
                sequence = test_sequences.pop()
                count = int(sequence.get('units_required')) - work_order.units.filter(
                    procedureresult__test_sequence_definition__id=sequence.get('test_sequence_id')).distinct().count()
                test_sequence = TestSequenceDefinition.objects.get(id=sequence.get('test_sequence_id'))
                while (len(params) and count):
                    key = params.pop()
                    # TODO: Wrap this with exception handler
                    unit = Unit.objects.get(id=key)
                    # This error handling sucks
                    if unit.workorder_set.all().count():  # already assigned to a work order
                        errors.append(
                            "Error: Unit {} already assigned to a work order".format(unit.serial_number)
                        )
                    else:
                        unit.tib = work_order.tib
                        unit.save()
                        work_order.units.add(unit)
                        work_order.save()
                    self.build_bucket(work_order, test_sequence, unit)
                    count -= 1

            if len(errors):
                return Response(errors)
        serializer = WorkOrderSerializer(work_order, many=False, context=self.context)
        return Response(serializer.data)

    # TODO: Decide if we keep this or move it
    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def link_units(self, request, pk=None):
        """
        This action endpoint is used to link units to the work order
        [
            "1","2"
        ]
        where the numbers represent a unit ID to link
        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            errors = []
            for key in params:
                # TODO: Wrap this with exception handler
                unit = Unit.objects.get(id=key)
                # This error handling sucks
                if unit.workorder_set.all().count():  # already assigned to a work order
                    errors.append(
                        "Error: Unit {} already assigned to a work order".format(unit.serial_number)
                    )
                else:
                    unit.tib = work_order.tib
                    unit.save()
                    work_order.units.add(unit)
                    work_order.save()
            if len(errors):
                return Response(errors)
        serializer = WorkOrderSerializer(work_order, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=WorkOrderSerializer,
            permission_classes=(ConfiguredPermission,)
            )
    def unlink_units(self, request, pk=None):
        """
        This action endpoint is used to unlink units from the work order
        [
        "1","2"
        ]
        """
        self.context = {'request': request}
        work_order = WorkOrder.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for key in params:
                unit = Unit.objects.get(id=key)
                work_order.units.remove(unit)
                work_order.save()
                # If there is any history for this unit in this project, leave it alone
                if project_history(unit, work_order.project):
                    continue
                else:
                    # This cleanses everything:
                    for procedure_result in work_order.procedureresult_set.filter(unit=unit):
                        for step_result in procedure_result.stepresult_set.all():
                            for measurement_result in step_result.measurementresult_set.all():
                                measurement_result.delete()
                            step_result.delete()
                        procedure_result.delete()

        serializer = WorkOrderSerializer(work_order, many=False, context=self.context)
        return Response(serializer.data)
