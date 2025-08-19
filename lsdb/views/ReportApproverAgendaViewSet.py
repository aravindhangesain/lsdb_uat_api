from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
import csv
from django.http import HttpResponse


class ReportApproverAgendaViewSet(viewsets.ModelViewSet):
    queryset = ReportApproverAgenda.objects.filter(flag=True)
    serializer_class = ReportApproverAgendaSerializer
    
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def date_verified(self, request, pk=None):
        date_verified = request.data.get("date_verified")
        verified_comment = request.data.get("verified_comment")
        if not date_verified:
            return Response({"error": "Approver Data Verification is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda = ReportApproverAgenda.objects.filter(report_result=report_result,flag=True).first()

        if agenda:
            agenda.date_verified = date_verified
            agenda.verified_comment = verified_comment
            agenda.user = user
            agenda.save()
        else:
            ReportApproverAgenda.objects.create(
                report_result=report_result,
                date_verified=date_verified,
                user=user,
                verified_comment=verified_comment
            )
        try:
            customer = report_result.work_order.project.customer.name
            project_number = report_result.work_order.project.number
            bom = report_result.work_order.name
            writer_user = reviewer_user = approver_user = None
            report_file = ReportFileTemplate.objects.filter(report_result=report_result).last()
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
                writer_agenda = ReportWriterAgenda.objects.get(report_result=report_result)
                contractually_obligated_date = (
                    writer_agenda.contractually_obligated_date.strftime('%Y-%m-%d %H:%M:%S')
                    if writer_agenda.contractually_obligated_date else "Not Set"
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
            <p>The <strong>Data Verification</strong> has been completed by
            <strong>{approver_user.get_full_name() or approver_user.username}</strong>
            for <strong>Report: {report_file.name}</strong>.</p>
            <p><strong>Details:</strong></p>
            <table style="border-collapse: collapse;">
            <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
            <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
            <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
            <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
            <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
            <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
            <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
            <tr><td><strong>Verified Date:</strong></td><td>&nbsp;&nbsp;{date_verified}</td></tr>
            <tr><td><strong>Contractually Obligated Date:</strong></td><td>&nbsp;&nbsp;{contractually_obligated_date}</td></tr>
            </table>
            <p><strong>Regards,<br/>PVEL System</strong></p>
            """
            email = EmailMessage(
                subject=f'[PVEL] Data Verification Completed - Project {project_number}',
                body=email_body,
                from_email='support@pvel.com',
                to=recipient_list
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
        except Exception as e:
            return Response({
                "error": "Data verified and saved, but failed to send email.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ReportApproverAgendaSerializer(agenda,context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def date_approved(self, request, pk=None):
        date_approved = request.data.get("date_approved")
        approved_comment = request.data.get("approved_comment")
        if not date_approved:
            return Response({"error": "Data Approved Verification is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda = ReportApproverAgenda.objects.filter(report_result=report_result,flag=True).first()
        if agenda:
            agenda.date_approved = date_approved
            agenda.approved_comment = approved_comment
            agenda.user = user
            agenda.save()
        else:
            ReportApproverAgenda.objects.create(
                report_result=report_result,
                date_approved=date_approved,
                user=user,
                approved_comment=approved_comment
            )
        try:
            customer = report_result.work_order.project.customer.name
            project_number = report_result.work_order.project.number
            bom = report_result.work_order.name
            report_file = ReportFileTemplate.objects.filter(report_result=report_result).last()
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
                writer_agenda = ReportWriterAgenda.objects.get(report_result=report_result)
                contractually_obligated_date = writer_agenda.contractually_obligated_date.strftime('%Y-%m-%d %H:%M:%S') if writer_agenda.contractually_obligated_date else "Not Set"
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
            <p>The <strong>Data</strong> has been Approved by <strong>{approver_user.get_full_name() or approver_user.username}</strong> for <strong>Report: {report_file.name}</strong>.</p>
            <p><strong>Details:</strong></p>
            <table style="border-collapse: collapse;">
                <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
                <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
                <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
                <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
                <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
                <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
                <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
                <tr><td><strong>Approved Date:</strong></td><td>&nbsp;&nbsp;{date_approved}</td></tr>
                <tr><td><strong>Contractually Obligated Date:</strong></td><td>&nbsp;&nbsp;{contractually_obligated_date}</td></tr>
            </table>
            <p><strong>Regards,<br/>PVEL System</strong></p>
            """
            email = EmailMessage(
                subject=f'[PVEL] Data Approved By Approver - Project {project_number}',
                body=email_body,
                from_email='support@pvel.com',
                to=recipient_list
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
        except Exception as e:
            return Response({
                "error": "Data verified and saved, but failed to send email.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ReportApproverAgendaSerializer(agenda,context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def date_delivered(self, request, pk=None):
        date_delivered = request.data.get("date_delivered")
        delivered_comment = request.data.get("delivered_comment")
        if not date_delivered:
            return Response({"error": "Data Delivered is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda = ReportApproverAgenda.objects.filter(report_result=report_result,flag=True).first()
        if agenda:
            agenda.date_delivered = date_delivered
            agenda.delivered_comment = delivered_comment
            agenda.user = user
            agenda.save()
        else:
            ReportApproverAgenda.objects.create(
                report_result=report_result,
                date_delivered=date_delivered,
                user=user,
                delivered_comment=delivered_comment
            )
        try:
            customer = report_result.work_order.project.customer.name
            project_number = report_result.work_order.project.number
            bom = report_result.work_order.name
            report_file = ReportFileTemplate.objects.filter(report_result=report_result).last()
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
                writer_agenda = ReportWriterAgenda.objects.get(report_result=report_result)
                contractually_obligated_date = (
                    writer_agenda.contractually_obligated_date.strftime('%Y-%m-%d %H:%M:%S')
                    if writer_agenda.contractually_obligated_date else "Not Set"
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
            <p>The <strong>Ready For Delivery-</strong><strong>ReportResult: {report_file.name}</strong>.</p>
            <p><strong>Details:</strong></p>
            <table style="border-collapse: collapse;">
            <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
            <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
            <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
            <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
            <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
            <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
            <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
            <tr><td><strong>Delivered Date:</strong></td><td>&nbsp;&nbsp;{date_delivered}</td></tr>
            <tr><td><strong>Contractually Obligated Date:</strong></td><td>&nbsp;&nbsp;{contractually_obligated_date}</td></tr>
            </table>
            <p><strong>Regards,<br/>PVEL System</strong></p>
            """
            email = EmailMessage(
                subject=f'[PVEL] Ready for Delivery - Project {project_number}',
                body=email_body,
                from_email='support@pvel.com',
                to=recipient_list
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
        except Exception as e:
            return Response({
                "error": "Date delivered saved, but failed to send email.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = ReportApproverAgendaSerializer(agenda,context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @transaction.atomic
    @action(detail=False,methods=["post","get"]) 
    def send_to_delivered_grid(self,request):
        report_result_id=request.data.get('report_result_id')
        comments = request.data.get('comments')
        if report_result_id is not None:
            reportwritertable=ReportApproverAgenda.objects.get(report_result_id=report_result_id,flag=True)
            reportwritertable.flag=False
            reportwritertable.comments = comments
            reportwritertable.comment_flag = 'Approved'
            reportwritertable.save()
            try:
                report_result = ReportResult.objects.get(id=report_result_id)
                customer = report_result.work_order.project.customer.name
                project_number = report_result.work_order.project.number
                bom = report_result.work_order.name
                report_file = ReportFileTemplate.objects.filter(report_result=report_result).last()
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
                <p>Hi Team,</p>
                <p>The <strong>ReportResult: {report_file.name}</strong> has been approved.</p>
                <p><strong>Details:</strong></p>
                <table style="border-collapse: collapse;">
                <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
                <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
                <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
                <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
                <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
                <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
                <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
                </table>
                <p><strong>Regards,<br/>PVEL System</strong></p>
                """
                email = EmailMessage(
                    subject=f'[PVEL]Status of the Report(Approved) - Project {project_number}',
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
            return Response({"message": "Report Moved to delivered grid"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic
    @action(detail=False,methods=["post","get"]) 
    def reject(self,request):
        report_result_id=request.data.get('report_result_id')
        comments = request.data.get('comments')
        if report_result_id:
            reportapprovertable=ReportApproverAgenda.objects.get(report_result_id=report_result_id, flag=True)
            reportapprovertable.flag=False
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
                report_file = ReportFileTemplate.objects.filter(report_result=report_result).last()
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
                <p>Hi Team,</p>
                <p>The <strong>Report: {report_file.name}</strong> has been rejected.</p>
                <p><strong>Details:</strong></p>
                <table style="border-collapse: collapse;">
                <tr><td><strong>Customer:</strong></td><td>&nbsp;&nbsp;{customer}</td></tr>
                <tr><td><strong>BOM:</strong></td><td>&nbsp;&nbsp;{bom}</td></tr>
                <tr><td><strong>Project Number:</strong></td><td>&nbsp;&nbsp;{project_number}</td></tr>
                <tr><td><strong>Report Writer:</strong></td><td>&nbsp;&nbsp;{report_writer}</td></tr>
                <tr><td><strong>Report Approver:</strong></td><td>&nbsp;&nbsp;{report_approver}</td></tr>
                <tr><td><strong>Report Reviewer:</strong></td><td>&nbsp;&nbsp;{report_reviewer}</td></tr>
                <tr><td><strong>Report Type:</strong></td><td>&nbsp;&nbsp;{report_type}</td></tr>
                </table>
                <p><strong>Regards,<br/>PVEL System</strong></p>
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
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        
    # @transaction.atomic
    # @action(detail=False,methods=["post","get"]) 
    # def rejected_reports_history(self,request):
        
    @action(detail=False, methods=["get"],url_path='download_report_approver_agenda')
    def download_report_approver_agenda(self, request):
        queryset = ReportApproverAgenda.objects.filter(flag=True)
        if not queryset.exists():
            return Response({"detail": "No data to export."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReportApproverAgendaSerializer(queryset, many=True,context={'request': request})
      
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ReportApproverAgenda.csv"'
        writer = csv.writer(response)
        headers = [
            'Approver Name',
            'Report Type',
            'Report',
            'Customer Name',
            'Project Number',
            'Report Version Number',
            'BOM Type',
            'Project Manager',
            'Author Name',
            'NTP Date',
            'Contractually Obligated Date',
            'Date Entered',
            'Date Verified',
            'Date Approved',
            'Date Delivered'
            ]   
        writer.writerow(headers)
        for item in serializer.data:
            writer.writerow([
                item.get('approver_name'),
                item.get('report_type_definition_name'),
                item.get('report_result_id'),
                item.get('customer_name'),
                item.get('project_number'),
                item.get('report_version_number'),
                item.get('bom'),
                item.get('project_manager_name'),
                item.get('author_name'),
                item.get('ntp_date'),
                item.get('contractually_obligated_date'),
                item.get('date_entered'),
                item.get('date_verified'),
                item.get('date_approved'),
                item.get('date_delivered'),
            ])

        return  response
        