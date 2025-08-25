from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response

class ReportChecklistNoteViewSet(viewsets.ModelViewSet):
    queryset = ReportChecklistNote.objects.all()
    serializer_class = ReportChecklistNoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-report')
    def by_checklistreport(self, request):
            report_id = request.query_params.get('report_result_id')
            checklist_id = request.query_params.get('checklist_id')
            checklist_report_id = request.query_params.get('checklist_report_id')
            if not all([report_id, checklist_id, checklist_report_id]):
                return Response({"error": "Missing some parameters"}, status=400)
            notes = self.queryset.filter(report_id=report_id, checklist_id=checklist_id, checklist_report_id=checklist_report_id).order_by('-datetime')
            serializer = self.get_serializer(notes, many=True)
            return Response(serializer.data)