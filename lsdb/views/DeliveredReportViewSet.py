from rest_framework import viewsets,status
from lsdb.models import ReportApproverAgenda
from lsdb.serializers import ReportApproverAgendaSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
from lsdb.models import *
from lsdb.serializers import *

class DeliveredReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportApproverAgenda.objects.filter(history_flag=True)
    serializer_class = ReportApproverAgendaSerializer

    @transaction.atomic
    @action(detail=False,methods=["post","get"]) 
    def reject(self,request):
        report_result_id=request.data.get('report_result_id')
        comments = request.data.get('comments')
        if report_result_id:
            reprt_type_id= report_result.report_type_definition.id
            report_team = ReportTeam.objects.get(report_type_id=reprt_type_id)

            if report_team.approver.username == request.user.username or request.user.is_superuser==True:
                reportapprovertable=ReportApproverAgenda.objects.get(report_result_id=report_result_id, history_flag=True)
                reportapprovertable.flag=False
                reportapprovertable.history_flag=False
                reportapprovertable.comments = comments
                reportapprovertable.comment_flag = 'Rejected'
                reportapprovertable.save()
                reportresult=ReportResult.objects.get(id=report_result_id)
                reportresult.is_approved=False
                reportresult.save()
                reportwriteragenda=ReportWriterAgenda.objects.get(report_result_id=report_result_id)
                reportwriteragenda.is_approved=False
                reportwriteragenda.save()
                try:
                    report_result = ReportResult.objects.get(id=report_result_id)
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
                    recipient_list = []
                    seen_emails = set()
                    for usr in [writer_user, reviewer_user, approver_user]:
                        if usr and usr.email and usr.email not in seen_emails:
                            recipient_list.append(usr.email)
                            seen_emails.add(usr.email)
                    email_body = f"""
                    <p><strong>Hi Team,</strong></p>
                    <p>The <strong>Report</strong> has been rejected.</p>
                    <p><strong>Details:</strong></p>
                    <table style="border-collapse: collapse;">
                    <tr><td><strong>File Name:</strong> {report_file.name}</td></tr>
                    <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
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
                        subject=f'[PVEL]Status of the Report(Rejected) - Project {project_number}',
                        body=email_body,
                        from_email='support@pvel.com',
                        to=recipient_list
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=False)
                except Exception as e:
                    return Response({
                        "error": "Date delivered saved, but failed to send email.",
                        "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({"message": "Report Moved to Writer grid"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "You are not authorized to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)