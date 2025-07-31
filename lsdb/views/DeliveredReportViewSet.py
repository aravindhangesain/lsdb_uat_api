from rest_framework import viewsets
from lsdb.models import ReportApproverAgenda
from lsdb.serializers import ReportApproverAgendaSerializer


class DeliveredReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReportApproverAgenda.objects.filter(flag=False)
    serializer_class = ReportApproverAgendaSerializer