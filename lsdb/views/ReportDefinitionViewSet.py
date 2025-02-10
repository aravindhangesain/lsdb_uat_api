from rest_framework import viewsets
from lsdb.models import ReportDefinition
from lsdb.serializers import ReportDefinitionSerializer

class ReportDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ReportDefinition.objects.all()
    serializer_class = ReportDefinitionSerializer