from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class ReportApproverNoteViewSet(viewsets.ModelViewSet):
    queryset = ReportApproverNote.objects.all()
    serializer_class = ReportApproverNoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)