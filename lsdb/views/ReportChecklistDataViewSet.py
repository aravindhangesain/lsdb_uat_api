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
        
        if not report_id or not checklist_report_id or not isinstance(checklist_data, list):
            return Response({"error": "Invalid input data"}, status=400)
        
        created_items = []
        for item in checklist_data:
            checklist_id = item.get('checklist_id')            
            if not checklist_id:
                continue
            
            report_checklist_data = ReportChecklistData.objects.create(
                report_id=report_id,
                checklist_report_id=checklist_report_id,
                checklist_id=checklist_id,
                status=True,
            )
            created_items.append(report_checklist_data)
        
        serializer = self.get_serializer(created_items, many=True)
        return Response(serializer.data, status=201)

