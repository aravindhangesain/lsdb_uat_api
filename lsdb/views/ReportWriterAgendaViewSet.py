from rest_framework import viewsets
from lsdb.models import ReportResult
from lsdb.serializers import ReportWriterAgendaSerializer

class ReportWriterAgendaViewSet(viewsets.ModelViewSet):
    queryset = ReportResult.objects.filter(hex_color='#4ef542')
    serializer_class = ReportWriterAgendaSerializer

    