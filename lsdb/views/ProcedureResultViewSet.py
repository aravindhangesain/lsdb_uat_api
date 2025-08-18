import json
import math
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.utils import timezone
from lsdb.utils import ExcelFile
from django.contrib.auth.models import User
from django.db.models import Q, Max
from io import BytesIO
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMessage


from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.status import (HTTP_400_BAD_REQUEST)

from lsdb.models import Asset, ProcedureExecutionOrder, ReportResult
from lsdb.models import Disposition, DispositionCode
from lsdb.models import Unit
from lsdb.models import Note
from lsdb.models import MeasurementResult
from lsdb.models import ProcedureResult,FinalProcedure
from lsdb.models import StepResult,LocationLog
from lsdb.models import StepDefinition
from lsdb.models import *

from lsdb.serializers import DispositionCodeListSerializer
from lsdb.serializers import NoteSerializer
from lsdb.serializers import ResultStatsSerializer
from lsdb.serializers import StepResultSerializer
from lsdb.serializers import ProcedureResultSerializer
from lsdb.serializers import ProcedureResultStressSerializer
from lsdb.serializers import ProcedureResultVerificationSerializer
from lsdb.serializers import TransformIVCurveSerializer
from lsdb.serializers import ProcedureWorkLogSerializer
from lsdb.permissions import ConfiguredPermission
from lsdb.utils import RetestUtils
# from lsdb.utils.NoteUtils import create_note


class ProcedureResultViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ProcedureResult to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ProcedureResult.objects.all()
    serializer_class = ProcedureResultSerializer
    permission_classes = [ConfiguredPermission]

    @action(detail=False, methods=['get',],
        serializer_class=DispositionCodeListSerializer,
    )
    def dispositions(self, request, pk=None):
        self.context={'request':request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='procedure_results'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=StepResultSerializer,
    )
    def add_step(self, request, pk=None):
        """
        This action accepts a minimum amount of data in order to POST results to a NEW Step Result attached to this procedure_result.
        POST:
        {
            "notes": string (optional)
            "step_definition": ID (Required)
            "execution_number": (blank=False, null=False)
            "disposition": ID (optional)
            "start_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format (optional)
            "test_step_result": ID (optional) points to step being replaced in retest
            "archived": boolean (default: false) only used for retest
            "name": string (default: step_definition.name)
            "description": string (optional)
            "step_number": string (optional)
            "linear_execution_group": float (optional)
        }
        """
        self.context={'request':request}
        procedure_result = ProcedureResult.objects.get(id=pk)
        # from django.urls import resolve
        if request.method == 'POST':
            params = request.data

            disposition = params.get('disposition')
            if disposition and (type(disposition) == int):
                disposition = Disposition.objects.get(id=disposition)

            # This is the only strictly required param from the POST:
            step_definition = params.get('step_definition')
            if type(step_definition) == int:
                step_definition = StepDefinition.objects.get(id=step_definition)
            # try:
            #     step_definition = StepDefinition.objects.get(id=resolve(step_definition).kwargs.get('pk'))
            # except IntegrityError:
            #     print('huh')

            step_result = StepResult.objects.create(
                notes = params.get('notes'),
                procedure_result = procedure_result,
                step_definition = step_definition,
                execution_number = params.get('execution_number',0),
                disposition = disposition,
                start_datetime = params.get('start_datetime'),
                duration = params.get('duration'),
                test_step_result = params.get('test_step_result'),
                archived = params.get('archived',False),
                name = params.get('name',step_definition.name),
                description = params.get('description'),
                step_number = params.get('step_number'),
                step_type = step_definition.step_type,
                linear_execution_group = params.get('linear_execution_group',0),
            )
            # print(step_result)
            for measurement_definition in step_definition.measurementdefinition_set.all():
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

            serializer = StepResultSerializer(step_result, many=False, context=self.context)
        else:
            # send error not 200
            serializer = ProcedureResultSerializer(procedure_result, many=False, context=self.context)
        return Response(serializer.data)

    # @transaction.atomic
    # @action(detail=True, methods=['get','post'],
    #     permission_classes=(ConfiguredPermission,),
    #     serializer_class = ProcedureResultSerializer,
    # )
    # def add_note(self, request, pk=None):
    #     """
    #     This action is used to add notes to a unit.
    #     POST:
    #     {
    #         "subject": "Unit note subject",
    #         "text": "Unit note text body",
    #         "type":$ID,
    #         "owner": $ID,
    #         "disposition": $ID,
    #         "labels": [$ID1, $ID2...],
    #         "groups": [$ID1, $ID2...],
    #         "tagged_users": [$ID1, $ID2...]
    #     }
    #     """
    #     self.context = {'request':request}
    #     procedure_result = ProcedureResult.objects.get(id=pk)
    #     if request.method == "POST":
    #         params = json.loads(request.body)
    #         noteParams = {
    #             "model" : "procedureresult",
    #             "pk" : pk,
    #             "user" : request.user,
    #             "subject" : params.get('subject'),
    #             "text" : params.get('text'),
    #             "note_type" : params.get('type'),
    #         }
    #         if params.get('owner') and params.get('owner') != -1:
    #             noteParams["owner"] = User.objects.get(id=params.get('owner'))
    #         if params.get('disposition') and params.get('disposition')!= -1 :
    #             noteParams["disposition"] =Disposition.objects.get(id=params.get('disposition'))
    #         newNote = create_note(
    #             **noteParams
    #         )
    #         # ProcedureResults need to trickle notes up to Unit and Project:
    #         procedure_result.work_order.project.notes.add(newNote)
    #         procedure_result.unit.notes.add(newNote)
    #         newNote.labels.set(params.get('labels'))
    #         newNote.groups.set(params.get('groups'))
    #         newNote.tagged_users.set(params.get('tagged_users'))
    #         newNote.save()
    #         serializer = NoteSerializer(newNote,many=False, context=self.context)
    #     else:
    #         serializer = NoteSerializer([], many=True, context=self.context)
    #     return Response(serializer.data)

    @action(detail=True, methods=['get',],
        serializer_class=NoteSerializer,
    )
    def notes(self, request, pk=None):
        procedure_result = ProcedureResult.objects.get(id=pk)
        self.context = {'request':request}
        serializer = NoteSerializer(procedure_result.notes.all(),many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def retest(self, request, pk=None):
        """
        This behaves the same as the manage_results/retest procedure except that any POST will do.
        """
        self.context={'request':request}
        if request.method == 'POST':
            retest = RetestUtils()
            return Response(retest.retest_procedure(request,pk))
        else:
            return Response(ProcedureResultSerializer(ProcedureResult.objects.get(id=pk),
            many=False, context=self.context).data)


    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=ProcedureResultSerializer,
    )
    def submit(self, request, pk=None):
        """
        Submitting a result here will verify that all of the un skipable steps are
        completed before allowing a "terminal" disposition to be set.
        Additionally, if the disposition is "in progress" the server will set the
        "work_in_progress_must_comply" flag to True. If the disposition is being changed
        from "in progress" we will unset the flag.
        Accepts a sparse POST of:
        {
        "disposition": ID,
        "start_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
        "end_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
        }
        """
        self.context={'request':request}
        result = ProcedureResult.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            if params.get('disposition'):
                disposition = Disposition.objects.get(id=params.get('disposition'))
                if disposition.complete:
                    # check all of your measurementresults
                    if (result.stepresult_set.all().count()) and ( # there are result children
                        result.stepresult_set.all().count() != result.stepresult_set.filter(Q(disposition__complete=True)|Q(allow_skip=True)).count()):
                        # error case:
                        return Response({'message':'One or more steps attached to this procedure are not complete and cannot be skipped'}, status = HTTP_400_BAD_REQUEST)
                # all good, set the disposition to the incoming one:
                result.disposition = disposition
                # if result.end_datetime == None:
                #     result.end_datetime = timezone.now()
            # WIP Flag:
            result.work_in_progress_must_comply = (disposition.name.lower() == "in progress")
            result.start_datetime = params.get('start_datetime', result.start_datetime)
            result.end_datetime = params.get('end_datetime', result.end_datetime)
            result.save()

            if ReportResult.objects.filter(work_order=result.work_order,hex_color='#f51111').exists():
                valid_report=ReportResult.objects.filter(work_order=result.work_order,hex_color='#f51111').exclude(data_ready_status__in=["Factory Witness","Define","Module Intake"]).first()

                if valid_report:
                    procedure_exec_name=valid_report.data_ready_status

                    valid_definitions=ProcedureExecutionOrder.objects.filter(execution_group_name=procedure_exec_name,test_sequence_id=result.test_sequence_definition.id).values_list('procedure_definition_id',flat=True)
                    
                    procedure_results = ProcedureResult.objects.filter(
                        name=procedure_exec_name,
                        work_order=result.work_order,
                        procedure_definition_id__in=valid_definitions,
                        test_sequence_definition_id=valid_report.test_sequence_definition.id
                    )
                    if not all(procedure.disposition_id in [2, 10, 20] for procedure in procedure_results):
                        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
                        return Response(serializer.data)
                    else:
                        datetime=timezone.now()
                        valid_report.hex_color='#4ef542'
                        valid_report.ready_datetime=datetime
                        valid_report.is_approved = False
                        valid_report.save()
                        try:
                            customer = valid_report.work_order.project.customer.name
                            project_number = valid_report.work_order.project.number
                            bom = valid_report.work_order.name
                            date_time = valid_report.ready_datetime
                            try:
                                report_team = ReportTeam.objects.get(report_type=valid_report.report_type_definition)
                                writer_user = report_team.writer
                                reviewer_user = report_team.reviewer
                                approver_user = report_team.approver or valid_report.work_order.project.project_manager
                            except ReportTeam.DoesNotExist:
                                writer_user = reviewer_user = approver_user = None
                            report_writer = writer_user.get_full_name() if writer_user else "Not Assigned"
                            report_reviewer = reviewer_user.get_full_name() if reviewer_user else "Not Assigned"
                            report_approver = approver_user.get_full_name() if approver_user else "Not Assigned"
                            try:
                                agenda = ReportWriterAgenda.objects.get(report_result=valid_report)
                                contractually_obligated_date = (
                                    agenda.contractually_obligated_date.strftime('%Y-%m-%d %H:%M:%S')
                                    if agenda.contractually_obligated_date
                                    else "Not Set"
                                )
                            except ReportWriterAgenda.DoesNotExist:
                                contractually_obligated_date = "Not Set"
                            recipient_list = []
                            seen_emails = set()
                            for usr in [writer_user, reviewer_user, approver_user]:
                                if usr and usr.email and usr.email not in seen_emails:
                                    recipient_list.append(usr.email)
                                    seen_emails.add(usr.email)
                            email_body = f"""
                                <p>Hi Team,</p>
                                <p>This Report has been moved to Writer's Agenda </p>
                                <p><strong>Details:</strong></p>
                                <table style="border-collapse: collapse;">
                                <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
                                <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
                                <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
                                <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
                                <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
                                <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
                                <tr><td><strong>Start Date:</strong></td><td>&nbsp;&nbsp;{date_time}</td></tr>
                                </table>
                                <p><strong>Regards,<br>PVEL System</strong></p>
                            """
                            email = EmailMessage(
                                subject='[PVEL] Tech Writer Start Date Set',
                                body=email_body,
                                from_email='support@pvel.com',
                                to=recipient_list,
                            )
                            email.content_subtype = "html"
                            email.send(fail_silently=False)
                        except Exception as e:
                            return Response(
                                {"error": "Date saved, but failed to send email.", "details": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )


        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)


    @action(detail=True,methods=['get'],
        permission_classes=(ConfiguredPermission,),
        serializer_class=ProcedureResultSerializer)
    def download(self, request, pk=None):
        # read the visualizer value of the current record to determine the shape
        # of the data to return.
        self.context = {'request':request}
        result = ProcedureResult.objects.get(id=pk)
        file = {}
        try:
            file = getattr(self, "_download_{}".format(result.procedure_definition.visualizer.name))(request, pk)
        except:
            'some error'
        return file

    def _download_colorimeter(self, request, pk=None):
        excel_file = ExcelFile()
        sheet = excel_file.workbook.active
        result = ProcedureResult.objects.get(id=pk)
        #Does not account for supersceded results
        result = result.stepresult_set.filter(disposition__isnull=False)
        result = result.first().measurementresult_set.filter(disposition__isnull=False)
        #Header Rows
        sheet.append([
            "Position",
            "L*",
            "A*",
            "B*"
        ])
        #Convert meassurement string to data values
        data = json.loads(result[0].result_string)
        data = data["values"]
        #Append values to sheet, calculate avg as we go
        l_val, a_val, b_val = [], [], []

        for value in data:
            row = [value["position"], value["l_value"], value["a_value"], value["b_value"]]
            l_val.append(value["l_value"])
            a_val.append(value["a_value"])
            b_val.append(value["b_value"])
            sheet.append(row)

        sheet.append(["Average", np.average(l_val), np.average(a_val), np.average(b_val)])

        sheet.append(["STD", np.std(l_val), np.std(a_val), np.std(b_val)])

        filename = 'ColorimeterReport-{}'.format(timezone.now().strftime('%b-%d-%Y-%H%M%S'))
        return excel_file.get_response(filename)

    def _download_diode(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
    def _download_el_image(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
    def _download_iam(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
    def _download_pan(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
    def _download_visual_inspection(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
    def _download_wet_leakage(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)

    # Transforming Visualizers
    def _download_stress(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultStressSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
    def _download_iv_curve(self, request, pk=None):
        # print('calling')
        result = ProcedureResult.objects.get(id=pk)
        serializer = TransformIVCurveSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
    

    @action(detail=False, methods=['post', 'get'],permission_classes=(AllowAny,))
    def valid_procedure(self, request):
        self.context = {'request': request}
        procedure_id = request.data.get('procedure_id')

        if not procedure_id:
            return Response({"message": "No procedure_id provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = ProcedureResult.objects.get(id=procedure_id)
        except ObjectDoesNotExist:
            return Response({"message": "No Procedure found"}, status=status.HTTP_404_NOT_FOUND)

        previous_results = ProcedureResult.objects.filter(
            linear_execution_group__lt=result.linear_execution_group,
            procedure_definition=result.procedure_definition,
            unit_id=result.unit_id
        )

        serialized_data = ProcedureWorkLogSerializer(previous_results, many=True, context=self.context).data
        return Response(serialized_data, status=status.HTTP_200_OK)
        
        
    @action(detail=False,methods=['post','get'])
    def flash_values(self, request):
        self.context = {'request': request}
        selected_procedure_id = request.data.get('selected_procedure_id')
        procedure_id=request.data.get('procedure_id')

        if procedure_id:
            FinalProcedure.objects.create(selected_procedure=selected_procedure_id,procedure=procedure_id)
        else:
            return Response({"error": "procedure_id is required."}, status=400)


        if not selected_procedure_id:
            return Response({"error": "selected_procedure_id is required."}, status=400)

        try:
            procedure = ProcedureResult.objects.get(id=selected_procedure_id)
            flash_measurements = MeasurementResult.objects.filter(
                step_result__procedure_result=procedure.id
            ).exclude(result_double__isnull=True)

            flash = {measurement.name: measurement.result_double for measurement in flash_measurements}
            # SelectedProcedure.objects.create()
            return Response({'flash_values': flash}, status=200)

        except ProcedureResult.DoesNotExist:
            return Response({"error": "Procedure not found."}, status=404)




    @action(detail=True, methods=['get'],
        permission_classes=(ConfiguredPermission,),
        serializer_class=ProcedureWorkLogSerializer)
    def view(self, request, pk=None):
        # Read the visualizer value of the current record to determine the shape of the data to return.
        self.context = {'request': request}
        result = ProcedureResult.objects.get(id=pk)
        visualized = {}

        try:
            visualized = getattr(self, "_view_{}".format(result.procedure_definition.visualizer.name))(request, pk)
        except Exception as e:
            print(f"Visualizer function error: {e}")

        try:
            previous_results = ProcedureResult.objects.filter(
                linear_execution_group__lt=result.linear_execution_group,
                procedure_definition=result.procedure_definition,
                unit_id=result.unit_id,
                # test_sequence_definition=result.test_sequence_definition,
            ).order_by('-linear_execution_group')
            for procedure_result in previous_results:
                flash_measurements = MeasurementResult.objects.filter(
                    step_result__procedure_result=procedure_result.id,
                ).exclude(result_double__isnull=True,)
                flash = {}
                for measurement in flash_measurements:
                    flash[measurement.name] = measurement.result_double
                visualized['previous_test'] = {
                    'pre_execution': procedure_result.linear_execution_group,
                    'prev_id': procedure_result.id,
                    'prev_name': procedure_result.name,
                    'flash_values': flash
                }
                if flash:
                    break
        except Exception as e:
            print(f"Error in visualizer: {e}")
        print("visualized:"+str(visualized))
        return Response(visualized)
    
    # @action(detail=True,methods=['get'],
    #     permission_classes=(ConfiguredPermission,),
    #     serializer_class=ProcedureWorkLogSerializer)
    # def view(self, request, pk=None):
    #     # read the visualizer value of the current record to determine the shape
    #     # of the data to return.
    #     self.context = {'request':request}
    #     result = ProcedureResult.objects.get(id=pk)
    #     visualized={}
    #     try:
    #         visualized = getattr(self, "_view_{}".format(result.procedure_definition.visualizer.name))(request, pk)
    #     except:
    #         'some error'
    #     try:
    #         previous_result = ProcedureResult.objects.filter(
    #             linear_execution_group__lt=result.linear_execution_group,
    #             procedure_definition=result.procedure_definition,
    #             unit_id=result.unit_id,
    #             test_sequence_definition=result.test_sequence_definition,
    #             name__icontains="Pre"
    #         ).order_by('-linear_execution_group').first()

    #         flash_measurements = MeasurementResult.objects.filter(
    #             step_result__procedure_result=previous_result.id,
    #             measurement_result_type__name__icontains='result_double'
    #         )
    #         flash = {}
    #         for measurement in flash_measurements:
    #             flash[measurement.name] = measurement.result_double
    #         visualized['previous_test'] = {
    #             'pre_execution':previous_result.linear_execution_group,
    #             'prev_id' : previous_result.id,
    #             'prev_name' : previous_result.name,
    #             'flash_values': flash
    #         }
    #     except Exception as e:
    #         print(f"Error in visualizer: {e}")

    #     return Response(visualized)
    
    # Base visualizers:
    def _view_colorimeter(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_diode(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_el_image(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_iam(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_pan(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_visual_inspection(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_wet_leakage(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultSerializer(result, many=False, context=self.context)
        return (serializer.data)

    # Transforming Visualizers
    def _view_stress(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = ProcedureResultStressSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_iv_curve(self, request, pk=None):
        result = ProcedureResult.objects.get(id=pk)
        serializer = TransformIVCurveSerializer(result, many=False, context=self.context)
        return serializer.data

    @action(detail=False, methods=['get'], 
        permission_classes=(ConfiguredPermission,), 
        serializer_class=ProcedureResultVerificationSerializer)
    def verify(self, request, pk=None):
        """
        Retrieve all records requiring verification, optionally filtering by location.
        """
        self.context = {'request': request}

        # Get the query parameter for location
        location_id = request.query_params.get('location', None)

        # Filter units requiring verification
        disposition = Disposition.objects.get(name__iexact='requires review')
        units = Unit.objects.filter(procedureresult__disposition=disposition).distinct()

        # If location_id is provided, filter further based on location
        if location_id:
            location_filtered_unit_ids = LocationLog.objects.filter(
                location_id=location_id,
                is_latest=True
            ).values_list('unit_id', flat=True)
            units = units.filter(id__in=location_filtered_unit_ids)

        # Serialize the filtered queryset
        serializer = self.serializer_class(units, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=False,methods=['get'],
        permission_classes=(ConfiguredPermission,),
        serializer_class=ProcedureWorkLogSerializer)
    def worklog(self, request, pk=None):
        """
        This action will GET data based on dates sent as query parameters.

        To set the range:
        start_datetime=YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
        end_datetime=YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,

        in order to dump an excel file of the same data for this range add:
        file=EXCEL

        GET /api/1.0/procedure_results/worklog/?start_datetime=2021-03-10&end_datetime=2021-03-11&file=excel
        """
        self.context = {'request':request}
        file = request.query_params.get('file','dummy')
        start_datetime = request.query_params.get('start_datetime',0)
        end_datetime = request.query_params.get('end_datetime',0)
        days = request.query_params.get('days',1)

        if start_datetime == 0 and end_datetime == 0:
            start_datetime = timezone.now() - timedelta(days=int(days))
            end_datetime = timezone.now()
        else:
            start_datetime = datetime.fromisoformat(start_datetime) + timedelta(days=1,hours=8)
            end_datetime = datetime.fromisoformat(end_datetime) + timedelta(days=1,hours=8)
            # this is still in zulu

        queryset = ProcedureResult.objects.filter(disposition__isnull=False,
            stepresult__archived=False,
            stepresult__disposition__isnull=False,
            stepresult__measurementresult__date_time__gte=start_datetime,
            stepresult__measurementresult__date_time__lte=end_datetime,
            ).distinct()
        serializer = ProcedureWorkLogSerializer(queryset, many=True, context=self.context)

        if file.upper() == 'EXCEL':
            wb = Workbook()
            sheet = wb.active
            sheet.append(['Project Number',
                        'Work Order',
                        'Serial Number',
                        'Test Sequence',
                        'Procedure',
                        'Disposition',
                        'Completion Date (UTC-8)',
                        'User',
                        'Characterization'])
            for row in serializer.data:
                result=dict(row)
                sheet.append([
                    result.get('project_number'),
                    result.get('work_order_name'),
                    str(result.get('serial_number')),
                    result.get('test_sequence_definition_name'),
                    result.get('procedure_definition_name'),
                    result.get('disposition_name'),
                    # timezone.make_aware(result.get('completion_date')),
                    timezone.make_naive(result.get('completion_date')) - timedelta(hours=8),
                    result.get('username'),
                    result.get('characterization_point')
                ])
            sheet.auto_filter.ref = sheet.dimensions
            mem_file = BytesIO(save_virtual_workbook(wb))
            # wb.save(mem_file)

            filename=timezone.now().strftime('%b-%d-%Y-%H%M%S')
            response = HttpResponse(mem_file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(filename)
            return response
        else:
            return Response(serializer.data)

    @action(detail=False,methods=['get'],
        permission_classes=(ConfiguredPermission,),
        serializer_class=ProcedureWorkLogSerializer)
    def procedure_stats(self, request, pk=None):
        self.context = {'request':request}
        file = request.query_params.get('file','dummy')
        start_datetime = request.query_params.get('start_datetime',0)
        end_datetime = request.query_params.get('end_datetime',0)
        # default to trailing 30 days
        days = request.query_params.get('days',120)
        facility = request.query_params.get('facility',None)

        if start_datetime == 0 and end_datetime == 0:
            start_datetime = timezone.now() - timedelta(days=int(days))
            end_datetime = timezone.now()
        else:
            start_datetime = datetime.fromisoformat(start_datetime) + timedelta(days=1,hours=8)
            end_datetime = datetime.fromisoformat(end_datetime) + timedelta(days=1,hours=8)
            # this is still in zulu
        queryset = ProcedureResult.objects.filter(disposition__isnull=False,
             stepresult__archived=False,
             stepresult__disposition__isnull=False,
             stepresult__measurementresult__date_time__gte=start_datetime,
             stepresult__measurementresult__date_time__lte=end_datetime,
             ).distinct()
        if facility:
            queryset = queryset.filter(stepresult__measurementresult__asset__location__name=facility)
        queryset = queryset.annotate(last_result = Max('stepresult__measurementresult__date_time'))
        master_data_frame = pd.DataFrame(list(queryset.values('last_result','procedure_definition__name')))
        master_data_frame['last_result']=master_data_frame['last_result'].dt.tz_convert("US/Pacific")
        master_data_frame['last_result']=master_data_frame['last_result'].dt.date
        df1 = pd.crosstab(master_data_frame['procedure_definition__name'],master_data_frame['last_result'].fillna(0))
        # df1.to_json(date_format='iso',orient='columns')
        final = []
        my_dict =  df1.to_dict()
        for day in my_dict:
            row={'date':day}
            row.update(my_dict[day].items())
            final.append(row)
        return Response(final)
