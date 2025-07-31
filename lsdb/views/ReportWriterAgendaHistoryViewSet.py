from lsdb.models import *
from lsdb.serializers import *
from rest_framework import viewsets

class ReportWriterAgendaHistoryViewSet(viewsets.ModelViewSet):
    queryset = ReportResult.objects.filter(hex_color='#4ef542',is_approved=True)
    serializer_class = ReportWriterAgendaSerializer