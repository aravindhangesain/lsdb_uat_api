from rest_framework import viewsets
from lsdb.models import ReportProductType
from lsdb.serializers import ReportProductTypeSerializer


class ReportProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ReportProductType.objects.all()
    serializer_class = ReportProductTypeSerializer