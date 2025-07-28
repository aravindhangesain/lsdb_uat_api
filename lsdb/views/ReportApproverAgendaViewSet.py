from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class ReportApproverAgendaViewSet(viewsets.ModelViewSet):
    queryset = ReportApproverAgenda.objects.filter(flag=True)
    serializer_class = ReportApproverAgendaSerializer

    