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
    @action(detail=False, methods=['post','get'])


    def add_reportchecklistdata(self, request):
        report_id = request.data.get('report_result_id')
        checklist_report_id = request.data.get('category_id')
        checklist_data = request.data.get('checklist_data', [])
        if request.method == 'POST':
            for item in checklist_data:
                ReportChecklistData.objects.create(
                    report_id=report_id,
                    checklist_report_id=checklist_report_id,
                    checklist_id=item["id"],
                    status=item["status"] if "status" in item else None,
                )
                
            return Response({"message": "ReportChecklistData entries created successfully."})
        
        elif request.method == 'PUT':
            
            for item in checklist_data:
                checklist=ReportChecklistData.objects.get(report_id=report_id,checklist_report_id=checklist_report_id,checklist_id=item["id"])
                checklist.status=item["status"]
                checklist.save()
            return Response({"message": "ReportChecklistData entries updated successfully."})

        else:
            return Response({"message": "Only POST method is allowed."})

    
            
            
        



            
        
        

