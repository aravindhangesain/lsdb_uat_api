from rest_framework import viewsets,status
from datetime import datetime as dt
from lsdb.models import ModuleIntakeDetails,ProcedureExecutionOrder, ReportResult,ReportExecutionOrder,WorkOrder,ReportSequenceDefinition,Disposition,ProcedureResult,Unit,TestSequenceDefinition,UnitReportResult
from lsdb.serializers import ReportResultSerilaizer,DispositionSerializer
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.response import Response
from django.db import connection
from django.utils import timezone
from lsdb.models import *
from django.core.mail import EmailMessage

from lsdb.serializers.ReportWriterAgendaSerializer import ReportWriterAgendaSerializer

class ReportResultViewSet(viewsets.ModelViewSet):
    serializer_class = ReportResultSerilaizer

    def get_queryset(self):
        queryset = ReportResult.objects.all().order_by('id')
        work_order_id = self.request.query_params.get('work_order_id')
        if work_order_id:
            queryset = queryset.filter(work_order_id=work_order_id)
        return queryset
    

    @transaction.atomic
    @action(detail=False,serializer_class=ReportResultSerilaizer,methods=['post','get'],)
    def create_report_result(self, request):
        work_order_id=request.data.get('work_order_id')
        report_sequence_definition_id=request.data.get('report_sequence_definition_id')
        # tsd_id=request.data.get('test_definition_id')
        if ReportResult.objects.filter(work_order_id=work_order_id).exists():
                return Response({"message":"Report already assigned for the given work-order"}, status=status.HTTP_404_NOT_FOUND)
        report_results=ReportExecutionOrder.objects.filter(report_sequence_definition_id=report_sequence_definition_id).order_by('execution_group_number')
        for result in report_results:
            workorder=WorkOrder.objects.get(id=work_order_id)
            report_definition=ReportSequenceDefinition.objects.get(id=report_sequence_definition_id)
            date_time=timezone.now()
            result_id=result.id
            tsd_id = result.test_definition.id if result.test_definition else None

            color_code=self.color_code(result_id,work_order_id,tsd_id)

            if color_code and color_code is not None:
                ReportResult.objects.create(work_order=workorder,report_sequence_definition=report_definition,
                                                report_execution_order_number=result.execution_group_number,
                                                product_type_definition=result.product_definition,
                                                report_type_definition=result.report_definition,
                                                data_ready_status=result.data_ready_status,reportexecution_azurefile=result.azure_file,
                                                hex_color=color_code,ready_datetime=date_time,test_sequence_definition_id=tsd_id)
            else:
                return Response({"message":"tsd_id not there in payload"}, status=status.HTTP_404_NOT_FOUND)
        queryset = ReportResult.objects.all()
        serializer = ReportResultSerilaizer(queryset,many=True, context={'request': request})
        return Response(serializer.data)
    

    def color_code(self, result_id, work_order_id, tsd_id):
        report = ReportExecutionOrder.objects.get(id=result_id)

        if report.data_ready_status in ['Module Intake']:
            
            project_id = WorkOrder.objects.filter(id=work_order_id).values_list('project_id', flat=True).first()
            
            bom_procedure_results=ProcedureResult.objects.filter(work_order_id=work_order_id,linear_execution_group=1).order_by('linear_execution_group')
            
            if all(procedure_result.disposition_id in [2,20,10,8,13] for procedure_result in bom_procedure_results):
                try:
                    project = Project.objects.get(id=project_id)
                    customer = project.customer.name if project.customer else "Not Set"
                    project_number = project.number
                    work_order = WorkOrder.objects.get(id=work_order_id)
                    bom = work_order.name

                    try:
                        report_team = ReportTeam.objects.get(report_type=report.report_definition_id)
                        writer_user = report_team.writer
                        reviewer_user = report_team.reviewer
                        approver_user = report_team.approver or project.project_manager
                    except ReportTeam.DoesNotExist:
                        writer_user = reviewer_user = approver_user = None

                    report_writer = writer_user.get_full_name() if writer_user else "Not Assigned"
                    report_reviewer = reviewer_user.get_full_name() if reviewer_user else "Not Assigned"
                    report_approver = approver_user.get_full_name() if approver_user else "Not Assigned"

                    recipient_list = []
                    seen_emails = set()
                    for usr in [writer_user, reviewer_user, approver_user]:
                        if usr and usr.email and usr.email not in seen_emails:
                            recipient_list.append(usr.email)
                            seen_emails.add(usr.email)

                    email_body = f"""
                        <p><strong>Hi Team,</strong></p>
                        <p> <strong>Module Intake</strong> steps are now completed for <strong>Project {project_number}</strong>. This Report has been moved to Report Writer's Agenda.</p>
                        <p><strong>Details:</strong></p>
                        <table style="border-collapse: collapse;">
                        <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
                        <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
                        <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
                        <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
                        <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
                        <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
                        </table>
                        <p><strong>Regards,</strong><br>PVEL System</p>
                    """

                    email = EmailMessage(
                        subject=f'[PVEL] Module Intake Completed - Project {project_number}',
                        body=email_body,
                        from_email='support@pvel.com',
                        to=recipient_list,
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=False)

                except Exception as e:
                    return Response(
                        {"error": "Module Intake completed but failed to send email.", "details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                return '#4ef542'  
            else:
                return '#f51111'

        elif report.data_ready_status in ['Factory Witness']:
            work_order = WorkOrder.objects.get(id=work_order_id)
            project_id = work_order.project.id
            if ProjectFactoryWitness.objects.filter(project_id=project_id,factory_witness=True).exists():
                return '#4ef542'
            else:
                return '#f51111'
        
        elif report.data_ready_status in ['Define']:
            return '#FAA405'
        else:
            if tsd_id:
                workorder = WorkOrder.objects.get(id=work_order_id)
                workorder_units = workorder.units.all()
                for unit in workorder_units:
                    unit_id = unit.id
                    procedure_def_name = report.data_ready_status
                    valid_procedure_definitions=ProcedureExecutionOrder.objects.filter(test_sequence_id=tsd_id,execution_group_name=procedure_def_name).values_list('procedure_definition_id',flat=True)
                    procedure_results = ProcedureResult.objects.filter(
                            name=procedure_def_name,
                            unit_id=unit_id,
                            procedure_definition_id__in=valid_procedure_definitions
                        )
                    if not all(procedure.disposition_id in [2, 10, 20] for procedure in procedure_results):
                            return '#f51111'
                return '#4ef542'
            else:
                return None
        

    @transaction.atomic
    @action(detail=False,methods=["patch","get"], url_path="update_report_result")
    def update_report_result(self, request):
        report_result_id=request.data.get('report_result_id')
        data_ready_status=request.data.get('data_ready_status')
        execution_number=request.data.get('execution_number')
        work_order_id=request.data.get('work_order_id')
        if report_result_id:
            try:
                report_result = ReportResult.objects.get(id=report_result_id)
            except ReportResult.DoesNotExist:
                return Response({"message": "ReportResult not found"}, status=status.HTTP_404_NOT_FOUND)
            is_procedure=request.data.get('is_procedure')
            if is_procedure is False:
                data=request.data.copy()
                patch_data = {
                    "report_result_id":report_result_id,
                    "data_ready_status":data_ready_status,
                    "work_order_id":work_order_id,
                    "is_procedure":data.pop('is_procedure',None)
                }
                serializer = ReportResultSerilaizer(report_result, data=data, partial=True, context={"request": request})
            if is_procedure is True:
                data = request.data.copy()
                patch_data = {
                                "execution_number":execution_number,
                                "data_ready_status":data_ready_status,
                                "report_result_id":report_result_id,
                                "serial_number": data.pop('serial_number', None),
                                "is_procedure": data.pop('is_procedure', None)
                            }
                serial_number=patch_data.get('serial_number')
                procedureresult_name=patch_data.get('data_ready_status')
                execution_number=patch_data.get('execution_number')
                unit_id=Unit.objects.filter(serial_number=serial_number).values_list('id',flat=True).first()
                UnitReportResult.objects.create(procedureresult_name=procedureresult_name,report_result_id=report_result_id,unit_id=unit_id,execution_group_number=execution_number)
                serializer = ReportResultSerilaizer(report_result, data=data, partial=True, context={"request": request})
            else:
                serializer = ReportResultSerilaizer(report_result, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "ReportResult updated successfully", "updated_response": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "ReportResult id not provided"}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=False,methods=["get"])
    def report_dispositions(self, request):
        dispositions=Disposition.objects.filter(id__in=[7,20,61,62])
        serializer=DispositionSerializer(dispositions,many=True,context={'request': request})
        return Response(serializer.data)
    

    @action(detail=False,methods=["post","get"])
    def get_unit_tsds(self, request):
        work_order_id = request.query_params.get('work_order_id')
        if not work_order_id:
            return Response({"error": "work_order_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT unit_id
                FROM lsdb_workorder_units
                WHERE workorder_id = %s
            """, [work_order_id])
            unit_ids = [row[0] for row in cursor.fetchall()]
            if not unit_ids:
                return Response({"No Unit Mapped with this work-order"},status=status.HTTP_200_OK)
            unit_tsd_list = []
            if unit_ids:
                for unit_id in unit_ids:
                    test_sequence_definition_id = ProcedureResult.objects.filter(unit_id=unit_id).values_list('test_sequence_definition_id', flat=True).first()
                    serial_number=Unit.objects.filter(id=unit_id).values_list('serial_number',flat=True).first()
                    test_sequence_definition_name=TestSequenceDefinition.objects.filter(id=test_sequence_definition_id).values_list('name',flat=True).first()
                    unit_tsd_list.append({
                        "unit_id": unit_id,
                        "serial_number":serial_number,
                        "test_sequence_definition_id": test_sequence_definition_id,
                        "test_sequence_definition_name":test_sequence_definition_name
                    })
                return Response(unit_tsd_list, status=status.HTTP_200_OK)
            
            
    @action(detail=False,methods=["post","get"])
    def get_unit_procedureresult_name(self, request):
        serial_number = request.query_params.get('serial_number')
        unit= Unit.objects.filter(serial_number=serial_number).first()
        proceduresults=[]
        if serial_number:
            procedures=ProcedureResult.objects.filter(unit_id=unit.id).order_by('name', 'id').distinct('name')
            if procedures:
                for procedure in procedures:
                    proceduresults.append({
                        "procedure_execution_order":procedure.linear_execution_group,
                        "name":procedure.name
                    })
                return Response(proceduresults,status=status.HTTP_200_OK)
            else:
                return Response({"No procedures for this unit"},status=status.HTTP_200_OK)
        else:
            return Response({"serial number is required"},status=status.HTTP_200_OK)
        
    
    @action(detail=False, methods=['post','get'])
    def pre_report_writer(self, request):
        incomplete_data_ready_status=ReportResult.objects.filter(hex_color='#f51111').exclude(data_ready_status__in=['Module Intake','Factory Witness','Define'])
        serializer=ReportWriterAgendaSerializer(incomplete_data_ready_status,many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

