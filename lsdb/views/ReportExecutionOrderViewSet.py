from rest_framework import viewsets
from lsdb.models import ReportExecutionOrder
from lsdb.serializers import ReportExecutionOrderSerializer

class ReportExecutionOrderViewSet(viewsets.ModelViewSet):
    queryset = ReportExecutionOrder.objects.all()
    serializer_class = ReportExecutionOrderSerializer


    