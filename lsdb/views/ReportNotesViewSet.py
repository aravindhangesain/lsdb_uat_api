from rest_framework import viewsets
from lsdb.models import ReportNotes
from lsdb.serializers import ReportNotesSerializer

class ReportNotesViewSet(viewsets.ModelViewSet):
    queryset = ReportNotes.objects.all()
    serializer_class = ReportNotesSerializer