from lsdb.models import *
from lsdb.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from django.core.mail import EmailMessage
import csv
from django.http import HttpResponse



class ReportWriterAgendaViewSet(viewsets.ModelViewSet):
    queryset = ReportResult.objects.filter(hex_color='#4ef542',is_approved=False)
    serializer_class = ReportWriterAgendaSerializer

    @action(detail=True, methods=["post"])
    def insert_date_time(self, request, pk=None):
        date_time = request.data.get("date_time")
        if not date_time:
            return Response({"error": "tech_writer_start_date is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            agenda = ReportWriterAgenda.objects.get(report_result=report_result)
        except ReportWriterAgenda.DoesNotExist:
            return Response({"error": "ReportWriterAgenda not found for the given ReportResult."},status=status.HTTP_404_NOT_FOUND)
        agenda.tech_writer_start_date = date_time
        agenda.user = user
        agenda.save()
        try:
            customer = report_result.work_order.project.customer.name
            project_number = report_result.work_order.project.number
            bom = report_result.work_order.name
            report_file = ReportFileTemplate.objects.filter(report=report_result).last()
            report_type = report_result.report_type_definition.name
            try:
                report_team = ReportTeam.objects.get(report_type=report_result.report_type_definition)
                writer_user = report_team.writer
                reviewer_user = report_team.reviewer
                approver_user = report_team.approver or report_result.work_order.project.project_manager
            except ReportTeam.DoesNotExist:
                writer_user = reviewer_user = approver_user = None
            report_writer = writer_user.get_full_name() if writer_user else "Not Assigned"
            report_reviewer = reviewer_user.get_full_name() if reviewer_user else "Not Assigned"
            report_approver = approver_user.get_full_name() if approver_user else "Not Assigned"
            try:
                agenda = ReportWriterAgenda.objects.get(report_result=report_result)
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
                <p>The Report<strong>Tech Writer Start Date</strong> has been set by <strong>{writer_user.get_full_name() or writer_user.username}</strong><strong> File Name: {report_file.name}</strong>.</p>
                <p><strong>Details:</strong></p>
                <table style="border-collapse: collapse;">
                <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
                <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
                <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
                <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
                <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
                <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
                <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
                <tr><td><strong>Start Date:</strong></td><td>&nbsp;&nbsp;{date_time}</td></tr>
                <tr><td><strong>Contractually Obligated Date:</strong></td><td>&nbsp;&nbsp;{contractually_obligated_date}</td></tr>
                </table>
                <p><strong>Regards,<br>PVEL System</strong></p>
            """
            email = EmailMessage(
                subject=f'[PVEL] Tech Writer Start Date Set - Project {project_number}',
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
        serializer = TechWriterStartDateSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=False,methods=["post","get"])
    def writer_reviewer_update(self, request):
        if request.method=='POST':
            user_id=request.user.id
            if user_id in [142,103,153]: 
                report_result_id=request.data.get('report_result_id')
                if report_result_id and report_result_id is not None:   
                    reportresult=ReportResult.objects.get(id=report_result_id)
                    reporttype_id=reportresult.report_type_definition.id
                    reportteam=ReportTeam.objects.get(report_type_id=reporttype_id)
                    reviewer_id = request.data.get('reviewer_id')
                    writer_id = request.data.get('writer_id')
                    if reviewer_id:
                        reportteam.reviewer = User.objects.get(id=reviewer_id)
                    if writer_id:
                        reportteam.writer = User.objects.get(id=writer_id)
                    reportteam.save()
                    return Response({"message": "updated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "reportresult_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "This user cannot be assigned for this task"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic
    @action(detail=False,methods=["post","get"]) 
    def send_to_aprover_grid(self,request):
        report_result_id=request.data.get('report_result_id')
        if report_result_id is not None:
            reportresult=ReportResult.objects.get(id=report_result_id)
            reportresult.is_approved=True
            reportresult.save()
            reportwritertable=ReportWriterAgenda.objects.get(report_result_id=report_result_id)
            reportwritertable.is_approved=True
            reportwritertable.save()
            ReportApproverAgenda.objects.create(flag=True,report_result_id=report_result_id)
            try:
                customer = reportresult.work_order.project.customer.name
                project_number = reportresult.work_order.project.number
                bom = reportresult.work_order.name
                report_file = ReportFileTemplate.objects.filter(report=reportresult).last()
                report_type = reportresult.report_type_definition.name

                try:
                    report_team = ReportTeam.objects.get(report_type=reportresult.report_type_definition)
                    writer_user = report_team.writer
                    reviewer_user = report_team.reviewer
                    approver_user = report_team.approver or reportresult.work_order.project.project_manager
                except ReportTeam.DoesNotExist:
                    writer_user = reviewer_user = approver_user = None
                report_writer = writer_user.get_full_name() if writer_user else "Not Assigned"
                report_reviewer = reviewer_user.get_full_name() if reviewer_user else "Not Assigned"
                report_approver = approver_user.get_full_name() if approver_user else "Not Assigned"
                try:
                    agenda = ReportWriterAgenda.objects.get(report_result=reportresult)
                    contractually_obligated_date = agenda.contractually_obligated_date.strftime('%Y-%m-%d %H:%M:%S') if agenda.contractually_obligated_date else "Not Set"
                except ReportWriterAgenda.DoesNotExist:
                    contractually_obligated_date = "Not Set"
                email_body = f"""
                <p>Hi Team,</p>
                <p>The <strong>Report</strong> has been moved to the <strong>Approver Grid</strong> by  <strong>{reviewer_user.get_full_name() or reviewer_user.username}</strong>.</p>
                <p><strong>File Name:</strong> {report_file.name}</p>
                <p><strong>Details:</strong></p>
                <table style="border-collapse: collapse;">
                    <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
                    <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
                    <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
                    <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
                    <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
                    <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
                    <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
                    <tr><td><strong>Contractually Obligated Date:</strong></td><td>&nbsp;&nbsp;{contractually_obligated_date}</td></tr>
                </table>
                <p><strong>Regards,<br>PVEL System</strong></p>
                """
                recipient_list = []
                seen_emails = set()
                for usr in [writer_user, reviewer_user, approver_user]:
                    if usr and usr.email and usr.email not in seen_emails:
                        recipient_list.append(usr.email)
                        seen_emails.add(usr.email)
                email = EmailMessage(
                subject=f'[PVEL] Report Moved to Approver Grid - Project {project_number}',
                body=email_body,
                from_email='support@pvel.com',
                to=recipient_list,
                )
                email.content_subtype = "html"
                email.send(fail_silently=False)
            except Exception as e:
                return Response({
                    "message": "Report moved, but failed to send email.",
                    "email_error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"message": "Report Moved to approver grid"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["get"],url_path='download_report_writer_agenda')
    def download_report_writer_agenda(self, request):
        queryset = ReportResult.objects.filter(hex_color='#4ef542',is_approved=False)
        if not queryset.exists():
            return Response({"detail": "No data to export."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReportWriterAgendaSerializer(queryset, many=True,context={'request': request})
      
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ReportWriterAgenda.csv"'
        writer = csv.writer(response)
        headers = [
            'Report Type',
            'Project Number',
            'Customer Name',
            'Project Manager',
            'NTP Date',
            'BOM Type',
            'priority',
            'contractually_obligated_date',
            'Data Verification Date',
            'PQP Version',
            'Tech Writer Start Date',
            'Report Writer Name',
            'Reviewer Name'
            ]   
        writer.writerow(headers)
        for item in serializer.data:
            writer.writerow([
                item.get('report_type_definition_name'),
                item.get('project_number'),
                item.get('customer_name'),
                item.get('project_manager_name'),
                item.get('ntp_date'),
                item.get('bom'),
                item.get('priority'),
                item.get('contractually_obligated_date'),
                item.get('data_verification_date'),
                item.get('pqp_version'),
                item.get('tech_writer_startdate'),
                item.get('report_writer_name'),
                item.get('report_reviewer_name'),
            ])

        return  response
    