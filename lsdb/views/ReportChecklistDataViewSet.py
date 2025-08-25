from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response

class ReportChecklistDataViewSet(viewsets.ModelViewSet):
    queryset = ReportChecklistData.objects.all()
    serializer_class = ReportChecklistDataSerializer
    
    def add_reportchecklistdata(self, request):
        report_id = request.data.get('report_id')
        checklist_report_id = request.data.get('checklist_report_id')
        checklist_data_ids = request.data.get('checklist_data', [])
        status = request.data.get('status', False)
        

        for checklist_data_id in checklist_data_ids:
            
            ReportChecklistData.objects.create(report_id=report_id,checklist_report_id=checklist_report_id,checklist_id=checklist_data_id,status=status)
                
        return Response({"message": "ReportChecklistData entries created successfully."})
            
        
    
            
            
        



            
        
        

