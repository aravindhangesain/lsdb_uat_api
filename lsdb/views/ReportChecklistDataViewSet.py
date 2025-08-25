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
        checklist_data = request.data.get('checklist_data', [])
        status = request.data.get('status')

        

        for item in checklist_data:
            ReportChecklistData.objects.create(
                report_id=report_id,
                checklist_report_id=checklist_report_id,
                checklist_id=item["id"],
                checklist_note_id=item["checklist_note_id"] if "checklist_note_id" in item else None,
                status=status
            )
            
        
    
            
            
        



            
        
        

