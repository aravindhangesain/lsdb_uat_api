from rest_framework import viewsets
from lsdb.models import ReportTypeDefinition
from lsdb.serializers import ReportTypeDefinitionSerializer

class ReportTypeDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ReportTypeDefinition.objects.all()
    serializer_class = ReportTypeDefinitionSerializer