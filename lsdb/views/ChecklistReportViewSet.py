from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class ChecklistReportViewSet(viewsets.ModelViewSet):
    queryset = ChecklistReport.objects.all()
    serializer_class = ChecklistReportSerializer

