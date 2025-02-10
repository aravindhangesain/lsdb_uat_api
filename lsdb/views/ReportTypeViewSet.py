from rest_framework import viewsets
from lsdb.models import ReportType
from lsdb.serializers import ReportTypeSerializer

class ReportTypeViewSet(viewsets.ModelViewSet):
    queryset = ReportType.objects.all()
    serializer_class = ReportTypeSerializer