from rest_framework import viewsets
from lsdb.models import ReportResult
from lsdb.serializers import ReportResultSerilaizer

class ReportResultViewSet(viewsets.ModelViewSet):
    queryset = ReportResult.objects.all()
    serializer_class = ReportResultSerilaizer