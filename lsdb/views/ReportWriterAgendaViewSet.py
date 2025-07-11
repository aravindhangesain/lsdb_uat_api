from rest_framework import viewsets
from lsdb.models import ReportWriterAgenda
from lsdb.serializers import ReportWriterAgendaSerializer

class ReportWriterAgendaViewSet(viewsets.ModelViewSet):
    queryset = ReportWriterAgenda.objects.all()
    serializer_class = ReportWriterAgendaSerializer

    