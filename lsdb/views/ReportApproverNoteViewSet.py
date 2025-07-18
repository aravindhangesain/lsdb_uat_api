from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response

class ReportApproverNoteViewSet(viewsets.ModelViewSet):
    queryset = ReportApproverNote.objects.all()
    serializer_class = ReportApproverNoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-report')
    def by_report(self, request):
        report_id = request.query_params.get('report_id')
        if not report_id:
            return Response({"error": "Missing report_id in query parameters"}, status=400)
        notes = self.queryset.filter(report_id=report_id)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)