import json
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from openpyxl.utils.dataframe import dataframe_to_rows

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.status import (HTTP_400_BAD_REQUEST)

from lsdb.models import StepResult
from lsdb.models import Disposition
from lsdb.models import DispositionCode
from lsdb.models import MeasurementResult
from lsdb.models import ProcedureResult
from lsdb.models import ProcedureDefinition
from lsdb.models import Project
from lsdb.models import MeasurementDefinition
from lsdb.models import ProcedureDefinition
from lsdb.models import TestSequenceDefinition
from lsdb.models import Unit

from lsdb.serializers import StepResultSerializer
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.serializers import ProcedureResultSerializer
from lsdb.permissions import ConfiguredPermission
from lsdb.utils import DeferredFile
from lsdb.utils import RetestUtils
from lsdb.utils.HasHistory import unit_completion, unit_revenue

class ManageResultViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows sensitive results to be viewed and changed.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepResult.objects.all()
    serializer_class = StepResultSerializer
    permission_classes = [ConfiguredPermission]

    @action(detail=False, methods=['get',],
        serializer_class=DispositionCodeListSerializer,
    )
    def dispositions(self, request, pk=None):
        self.context={'request':request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='step_results'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=False, methods=['get','post'],
        serializer_class=StepResultSerializer,
    )
    def retest_step(self, request, pk=None):
        """
        Accepts a sparse POST of:
        {
            "step_result":$ID
        }
        This action needs to mark the current step result archived=true
        """
        errors=[]
        self.context={'request':request}
        if request.method == "POST":
            params = json.loads(request.body)
            try:
                result = StepResult.objects.get(id=params.get('step_result'))
            except:
                errors.append(
                    "Error: requested step result {} does not exist".format(params.get('step_result'))
                )
                return Response(errors)
            # we have a step we're working on:
            new_step = StepResult.objects.create(
                name = result.name,
                procedure_result = result.procedure_result,
                step_definition = result.step_definition,
                execution_number = 0,
                disposition = None,
                start_datetime = None,
                duration = 0,
                test_step_result = None,
                archived = False,
                description = None,
                step_number = 0,
                step_type = result.step_definition.step_type,
                linear_execution_group = result.linear_execution_group,
                allow_skip = result.allow_skip,
            )
            for measurement_definition in result.step_definition.measurementdefinition_set.all():
                measurement_result = MeasurementResult.objects.create(
                    step_result = new_step,
                    measurement_definition = measurement_definition,
                    software_revision = 0.0,
                    disposition = None,
                    limit = measurement_definition.limit,
                    station = 0,
                    name = measurement_definition.name,
                    record_only = measurement_definition.record_only,
                    allow_skip = measurement_definition.allow_skip,
                    requires_review = measurement_definition.requires_review,
                    measurement_type = measurement_definition.measurement_type,
                    order = measurement_definition.order,
                    report_order = measurement_definition.report_order,
                    measurement_result_type = measurement_definition.measurement_result_type,
                )

            result.archived = True
            result.test_step_result = new_step
            result.save()
            serializer = StepResultSerializer(new_step, many=False, context=self.context)
        else:
            result = StepResult.objects.filter(
                disposition__isnull=False,
                disposition__complete=True,
            )
            serializer = StepResultSerializer(result, many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=False, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def insert_marker(self, request, pk=None):
        """
        This is an endpoint for a human or Ryan to interact with DRF. It inserts a completed procedure result into
        any unit test plan while blending in with the regular tests. This is a temporary patch to inject markers
        in for DCL units and long lost virgins.
        {​​​​​​​
        "serial_number":"001004",
        "leg":8
        }​​​​​
        """
        errors=[]
        self.context={'request':request}
        user = request.user
        completed = Disposition.objects.get(name__iexact='completed')
        marker = ProcedureDefinition.objects.get(name__iexact='marker')
        if request.method == "POST":
            params = json.loads(request.body)
            try:
                unit = Unit.objects.get(serial_number=params.get('serial_number'))
            except:
                errors.append(
                    "Error: Serial number not found"
                )
                return Response(errors)
            leg = unit.procedureresult_set.filter(linear_execution_group=params.get('leg')).distinct().first()
            if leg:
                # try:
                procedure_result = ProcedureResult.objects.create(
                    unit = unit,
                    name = leg.name,
                    disposition = completed,
                    group = marker.group,
                    work_order = leg.work_order,
                    procedure_definition = marker,
                    version = marker.version,
                    linear_execution_group = leg.linear_execution_group,
                    test_sequence_definition = leg.test_sequence_definition,
                    allow_skip = True,
                    start_datetime = timezone.now(),
                    end_datetime = timezone.now(),
                )
                # except:
                #     print('failed to create marker')
                #     continue
            else:
                errors.append('execution group not found:', params.get('leg'))
                return Response(errors)
            serializer = ProcedureResultSerializer(procedure_result, many=False, context=self.context)
        else:
            serializer = ProcedureResultSerializer([], many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=False, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def rerun_soak(self, request, pk=None):
        """
        This is a bit of a kluge, we should handle this better in the future.
        {
            "unit":$ID
        }
        In theory, when this is called the software should have a list of units that
        are being tested for stabilization.
        """
        errors=[]
        self.context={'request':request}
        new_procedures =[]
        if request.method == "POST":
            params = json.loads(request.body)
            # print(int(params.get('unit')))
            try:
                unit = Unit.objects.get(id=params.get('unit'))
            except:
                errors.append(
                    "Error: Unit not found"
                )
                return Response(errors)
            # Need to find all of the LATEST light soak 10's
            results = unit.procedureresult_set.filter(name__icontains='light soak >10').order_by('name')
            # Kluge: doing this via name is hackey
            # should be using repetiotion group, and repetitions to automate
            # a lot of this logic.
            last_run = int(results.last().name.split('#')[1])
            first_run = int(results.first().name.split('#')[1])
            offset = last_run * 2
            last_eg = results.last().linear_execution_group
            # get all of the procedures with EG > than this_run
            to_increment = unit.procedureresult_set.filter(linear_execution_group__gt = last_eg)
            for result in to_increment:
                result.linear_execution_group += 2
            ProcedureResult.objects.bulk_update(to_increment, ['linear_execution_group'])
            results = results.filter(name__endswith=first_run)
            this_run = int(last_run) +1
            for result in results:
                test_sequence = TestSequenceDefinition.objects.get(id=result.test_sequence_definition.id)
                procedures = test_sequence.procedureexecutionorder_set.filter(
                    execution_group_number = result.linear_execution_group,
                    procedure_definition = result.procedure_definition
                ).distinct()
                if procedures.count() != 1:
                    errors.append(
                            ["Error: requested procedure test definition {} incorrect.".format(test_sequence.id),
                            " {} procedures returned, should only ever be 1".format(procedures.count())]
                        )
                    print(errors)
                    raise IntegrityError
                    return Response(errors)
                # Start constructing the new procedure_result:
                execution = procedures.all()[0]
                procedure_result = ProcedureResult.objects.create(
                    unit = result.unit,
                    name = '{}#{}'.format(execution.execution_group_name.split('#')[0],this_run),
                    disposition = None,
                    group = execution.procedure_definition.group,
                    work_order = result.work_order,
                    procedure_definition = execution.procedure_definition,
                    version = execution.procedure_definition.version,
                    linear_execution_group = execution.execution_group_number + offset,
                    test_sequence_definition = test_sequence,
                    allow_skip = execution.allow_skip,
                )
                for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
                    step_result = StepResult.objects.create(
                        name = step_execution.execution_group_name,
                        procedure_result = procedure_result,
                        step_definition = step_execution.step_definition,
                        execution_number = 0,
                        disposition = None,
                        start_datetime = None,
                        duration = 0,
                        test_step_result = None,
                        archived = False,
                        description = None,
                        step_number = 0,
                        step_type = step_execution.step_definition.step_type,
                        linear_execution_group = step_execution.execution_group_number,
                        allow_skip = step_execution.allow_skip,
                    )
                    for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                        measurement_result = MeasurementResult.objects.create(
                            step_result = step_result,
                            measurement_definition = measurement_definition,
                            software_revision = 0.0,
                            disposition = None,
                            limit = measurement_definition.limit,
                            station = 0,
                            name = measurement_definition.name,
                            record_only = measurement_definition.record_only,
                            allow_skip = measurement_definition.allow_skip,
                            requires_review = measurement_definition.requires_review,
                            measurement_type = measurement_definition.measurement_type,
                            order = measurement_definition.order,
                            report_order = measurement_definition.report_order,
                            measurement_result_type = measurement_definition.measurement_result_type,
                        )

                new_procedures.append(procedure_result)
            serializer = ProcedureResultSerializer(new_procedures, many=True, context=self.context)
        else:
            serializer = ProcedureResultSerializer([], many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=False, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def record_completion(self, request, pk=None):
        """
        This action will mark a `procedure_result` as "Perfromed - Record only"
        Accepts a sparse POST of:
        {
            "procedure_result":$ID, // Required
            "start_datetime":YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ], // Optional, default Now()
            "end_datetime":YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ], // Optional, default Now()
            "user":username // Optional, default 'sysadmin'
        }
        This is NON-Destructive. Dates and user will not overwrite existing data.
        """
        errors=[]
        self.context={'request':request}
        if request.method == "POST":
            params = json.loads(request.body)
            try:
                record = Disposition.objects.get(name__iexact='performed - record only')
            except:
                errors.append(
                    "Error: required disposition configured incorrectly. Call Engineering!"
                )
                return Response(errors)
            try:
                result = ProcedureResult.objects.get(id=params.get('procedure_result'))
            except:
                errors.append(
                        "Error: requested procedure result {} does not exist".format(params.get('procedure_result'))
                    )
                return Response(errors)
            if not result.disposition == None:
                # This has a disposition, we don't want to change that
                errors.append(
                        "Error: requested procedure result {} has a disposition of {}, cowardly not writing".format(result.id,result.disposition.name)
                    )
                return Response(errors)
            # Should be working on a good POST body
            now_datetime = timezone.now()
            result.disposition = record
            if params.get('user'):
                try:
                    user = User.objects.get(username__iexact=params.get('user'))
                except:
                    errors.append(
                            "Error: requested user {} does not exist".format(params.get('user'))
                        )
                    return Response(errors)
            else:
                user = User.objects.get(username__iexact='sysadmin')
            if params.get('start_datetime') and result.start_datetime == None:
                result.start_datetime = params.get('start_datetime')
            elif result.start_datetime == None:
                result.start_datetime = now_datetime
            if params.get('end_datetime') and result.end_datetime == None:
                result.end = params.get('end_datetime')
            elif result.end_datetime == None:
                result.end_datetime = now_datetime
            # Now push that data down to all non-skipable everything.
            # TODO: Speed this up by using bulk_update() -- MD
            for step in result.stepresult_set.filter(allow_skip=False):
                step.disposition = record
                step.start_datetime = params.get('start_datetime',now_datetime)
                for measurement in step.measurementresult_set.filter(allow_skip=False):
                    measurement.disposition = record
                    measurement.date_time = now_datetime
                    measurement.user = user
                    measurement.start_datetime = params.get('start_datetime',now_datetime)
                    measurement.save()
                step.save()
            result.save()
            serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        else:
            serializer = ProcedureResultSerializer([], many=True, context=self.context)
        return Response(serializer.data)

        '''
        {
        "procedure_result":16,
        "start_datetime":"2021-09-21T22:45:43.937000Z",
        "end_datetime":"2021-09-23T22:45:43.937000Z",
        "user":"mark.davis@pvel.com"
        }
        '''
    @transaction.atomic
    @action(detail=False, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def retest_procedure(self, request, pk=None):
        """
        Accepts a sparse POST of:
        {
            "procedure_result":$ID
        }
        This action needs to mark the current step result archived=true
        """
        # Main code removed and pushed to utils/RetestUtils.py MD
        retest = RetestUtils()
        return Response(retest.retest_procedure(request))


    @transaction.atomic
    @action(detail=False, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def review(self, request, pk=None):
        """
        Updates the procedure_result disposition, records the current user in
        measurement_results as reviewed by the currently logged in user
        {
            "procedure_result":$ID,
            "disposition":$ID
        }
        """
        errors=[]
        self.context={'request':request}
        if request.method == "POST":
            params = json.loads(request.body)
            try:
                result = ProcedureResult.objects.get(id=params.get('procedure_result'))
            except:
                errors.append(
                        "Error: requested procedure result {} does not exist".format(params.get('procedure_result'))
                    )
                return Response(errors)
            try:
                disposition = Disposition.objects.get(id=params.get('disposition'))
            except:
                errors.append(
                        "Error: requested disposition {} does not exist".format(params.get('disposition'))
                    )
                return Response(errors)
            result.disposition = disposition
            result.save()
            for stepresult in result.stepresult_set.filter(disposition__isnull=False):
                stepresult.disposition = disposition
                stepresult.save()
                for measurement in stepresult.measurementresult_set.filter(disposition__isnull=False):
                    measurement.reviewed_by_user = request.user
                    measurement.review_datetime = timezone.now()
                    measurement.disposition = disposition
                    measurement.save()
            serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        else:
            serializer = ProcedureResultSerializer([], many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=False, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def revenue_report(self, request):
        deferred_file = DeferredFile()
        deferred_file.revenue_report(user=request.user)
        # excel_file = ExcelFile()
        # sheet = excel_file.workbook.active
        # report=[]
        # projects = Project.objects.filter(disposition__complete=False).prefetch_related('customer','workorder_set').order_by('customer__name')
        # # pandas dump to sheet:
        # # for row in dataframe_to_rows(df, index=False, header=True):
        # #     sheet.append(r)
        # # HUGE KLUGE! this is execeptionally unoptomized.
        # for project in projects:
        #     for work_order in project.workorder_set.all():
        #         row = [project.customer.name, project.number,work_order.name,0.0,0.0,0.0,0.0]
        #         for unit in work_order.units.all():
        #             complete = unit_completion(unit)
        #             if complete > 0:
        #                 revenue = unit_revenue(unit)
        #                 row[3]+=1 # units counted
        #                 row[4]+= revenue # revenue for the unit
        #                 row[5]+= revenue*complete/100 # recognizable revenue
        #                 row[6]+= complete
        #                 # print(revenue, complete, revenue*complete)
        #         if row[3] >0:
        #             row[6] = row[6]/row[3]
        #         # report.append(row)
        #         sheet.append(row)
        #         # print('"{0}","{1}","{2}",{3:.0f},{4:.3f},{5:.3f},{6:.3f}'.format(*row))
        # filename = 'RevenueReport-{}'.format(timezone.now().strftime('%b-%d-%Y-%H%M%S'))
        # return excel_file.get_response(filename)
        return Response({"message":"Your file will be available shortly"})
