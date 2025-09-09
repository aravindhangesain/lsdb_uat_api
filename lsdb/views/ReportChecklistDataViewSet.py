from gettext import translation
from rest_framework import viewsets,status
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.mail import EmailMessage
from datetime import datetime as time


class ReportChecklistDataViewSet(viewsets.ModelViewSet):
    queryset = ReportChecklistData.objects.all()
    serializer_class = ReportChecklistDataSerializer
    
    @transaction.atomic
    @action(detail=False, methods=['post','get','put'])
    def add_reportchecklistdata(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.method == 'POST':
            report_id = request.data.get('report_result_id')
            checklist_report_id = request.data.get('category_id')
            checklist_data = request.data.get('checklist_data', [])
            for item in checklist_data:
                ReportChecklistData.objects.create(
                    report_id=report_id,
                    checklist_report_id=checklist_report_id,
                    checklist_id=item["id"],
                    status=item["status"],
                )
            try:
                report_result = ReportResult.objects.get(id=report_id)
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
                # Build checklist table
                checklist_table = """
                    <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; margin-top:10px;">
                        <tr style="background-color:#f2f2f2;">
                            <th>Checklist ID</th>
                            <th>Category Name</th>
                            <th>Checklist Name</th>
                            <th>Status</th>
                            <th>Notes</th>
                        </tr>
                """
                for item in checklist_data:
                    checklist_data = CheckList.objects.filter(id=item["id"]).first()
                    if checklist_data:
                        category = checklist_data.category if checklist_data.category else "N/A"
                        check_point = checklist_data.check_point
                    else:
                        category = "N/A"
                        check_point = "N/A"
                    
                    checklist_note = ReportChecklistNote.objects.filter(
                        report_id=report_id,
                        checklist_report_id=checklist_report_id,
                        checklist_id=item["id"]
                    ).first()

                    notes = checklist_note.comment if checklist_note else "N/A"

                    checklist_table += f"""
                        <tr>
                            <td>{item.get("id")}</td>
                            <td>{category}</td>
                            <td>{check_point}</td>
                            <td>{item.get("status")}</td>
                            <td>{notes}</td>
                        </tr>
                    """
                checklist_table += "</table>"
                email_body = f"""
                    <p><strong>Hi Team,</strong></p>
                    <p><strong>Check List Data</strong> has been Added by <strong>{reviewer_user.get_full_name() or reviewer_user.username}</strong><Strong> for - File Name: {report_file.name}</strong>.</p>
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
                    <p><strong>Check List Details:</strong></p>
                    {checklist_table}
                    <p><strong>Regards,</strong><br>PVEL System</p>
                """
                email = EmailMessage(
                    subject=f'[PVEL] Check List Data has been Added - Project {project_number}',
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
                
            return Response({"message": "ReportChecklistData entries created successfully."})
        
        # Update checklist data
        elif request.method == 'PUT':
            report_id = request.data.get('report_result_id')
            checklist_report_id = request.data.get('category_id')
            checklist_data = request.data.get('checklist_data', [])
            for item in checklist_data:
                checklist=ReportChecklistData.objects.get(report_id=report_id,checklist_report_id=checklist_report_id,checklist_id=item["id"])
                if checklist:
                    
                    checklist.status=item["status"]
                    checklist.save()
                else:
                    return Response({"message": f"Checklist with report_id {report_id} and checklist_report_id{checklist_report_id} not found."}, status=404)
                try:
                    report_result = ReportResult.objects.get(id=report_id)
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
                    # Build checklist table
                    checklist_table = """
                        <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; margin-top:10px;">
                            <tr style="background-color:#f2f2f2;">
                                <th>Checklist ID</th>
                                <th>Category Name</th>
                                <th>Checklist Name</th>
                                <th>Status</th>
                                <th>Notes</th>
                            </tr>
                    """
                    for item in checklist_data:
                        checklist_data = CheckList.objects.filter(id=item["id"]).first()
                        if checklist_data:
                            category = checklist_data.category if checklist_data.category else "N/A"
                            check_point = checklist_data.check_point
                        else:
                            category = "N/A"
                            check_point = "N/A"
                        
                        checklist_note = ReportChecklistNote.objects.filter(
                            report_id=report_id,
                            checklist_report_id=checklist_report_id,
                            checklist_id=item["id"]
                        ).first()

                        notes = checklist_note.comment if checklist_note else "N/A"

                        checklist_table += f"""
                            <tr>
                                <td>{item.get("id")}</td>
                                <td>{category}</td>
                                <td>{check_point}</td>
                                <td>{item.get("status")}</td>
                                <td>{notes}</td>
                            </tr>
                        """
                    checklist_table += "</table>"
                    email_body = f"""
                        <p><strong>Hi Team,</strong></p>
                        <p><strong>Check List Data</strong> has been Updated by <strong>{reviewer_user.get_full_name() or reviewer_user.username}</strong><Strong> for - File Name: {report_file.name}</strong>.</p>
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
                        <p><strong>Check List Details:</strong></p>
                        {checklist_table}
                        <p><strong>Regards,</strong><br>PVEL System</p>
                    """
                    email = EmailMessage(
                        subject=f'[PVEL] Check List Data Updated - Project {project_number}',
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

            return Response({"message": "ReportChecklistData entries updated successfully."})

        elif request.method=='GET':
            report_id2 = request.query_params.get('report_result_id')
            # checklist_report_id2 = request.query_params.get('category_id')

            report_checklist_data = (
                ReportChecklistData.objects
                .filter(report_id=report_id2)
                .order_by('checklist__id')
            )

            final_response = {
                "category_id":report_checklist_data.first().checklist_report.id if report_checklist_data.exists() else None,
                "report_name": None,
                "check_list": []
            }

            
            category_map = {}

            for instance in report_checklist_data:
                notecount = ReportChecklistNote.objects.filter(
                    report_id=report_id2,
                    checklist_report_id=instance.checklist_report.id,
                    checklist=instance.checklist.id
                ).count()

                
                if final_response["report_name"] is None:
                    final_response["report_name"] = instance.checklist_report.report_name

                category_name = instance.checklist.category

                
                if category_name not in category_map:
                    category_entry = {
                        "category": category_name,
                        "check_point": []
                    }
                    final_response["check_list"].append(category_entry)
                    category_map[category_name] = category_entry

                
                category_map[category_name]["check_point"].append({
                    "id": instance.checklist.id,
                    "description": instance.checklist.check_point,
                    "status": instance.status,
                    "note_count": notecount
                })

            return Response({"results":[final_response]})

                
                

        else:
            return Response({"message": "Invalid request method."}, status=400)
        

    @transaction.atomic
    @action(detail=False, methods=['get'])   
    def pending_reportchecklistdata(self, request):
        
        
        if request.method=='GET':
            report_id2 = request.query_params.get('report_result_id')
            # checklist_report_id2 = request.query_params.get('category_id')

            report_checklist_data = (
                ReportChecklistData.objects
                .filter(report_id=report_id2,status=False)
                .order_by('checklist__id')
            )

            final_response = {
                "category_id":report_checklist_data.first().checklist_report.id if report_checklist_data.exists() else None,
                "report_name": None,
                "check_list": []
            }

            
            category_map = {}
    
            for instance in report_checklist_data:
                notecount = ReportChecklistNote.objects.filter(
                    report_id=report_id2,
                    checklist_report_id=instance.checklist_report.id,
                    checklist=instance.checklist.id
                ).count()

                
                if final_response["report_name"] is None:
                    final_response["report_name"] = instance.checklist_report.report_name

                category_name = instance.checklist.category

                
                if category_name not in category_map:
                    category_entry = {
                        "category": category_name,
                        "check_point": []
                    }
                    final_response["check_list"].append(category_entry)
                    category_map[category_name] = category_entry

                
                category_map[category_name]["check_point"].append({
                    "id": instance.checklist.id,
                    "description": instance.checklist.check_point,
                    "status": instance.status,
                    "note_count": notecount
                })

            return Response({"results":[final_response]})

                
                

        else:
            return Response({"message": "Invalid request method."}, status=400)

    
            
            
        



            
        
        

