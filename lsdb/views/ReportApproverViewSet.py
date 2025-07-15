from rest_framework import viewsets

from lsdb.models import ReportApprover
from lsdb.serializers import ReportApproverSerializer

class ReportApproverViewSet(viewsets.ModelViewSet):
    queryset = ReportApprover.objects.all()
    serializer_class = ReportApproverSerializer