from rest_framework import viewsets

from lsdb.models import ReportWriter
from lsdb.serializers import ReportWriterSerializer

class ReportWriterViewSet(viewsets.ModelViewSet):
    queryset = ReportWriter.objects.all()
    serializer_class = ReportWriterSerializer