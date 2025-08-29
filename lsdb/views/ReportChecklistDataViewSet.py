from gettext import translation
from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction


class ReportChecklistDataViewSet(viewsets.ModelViewSet):
    queryset = ReportChecklistData.objects.all()
    serializer_class = ReportChecklistDataSerializer
    
    @transaction.atomic
    @action(detail=False, methods=['post','get','put'])
    def add_reportchecklistdata(self, request):
        
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
                
            return Response({"message": "ReportChecklistData entries created successfully."})
        
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

    
            
            
        



            
        
        

