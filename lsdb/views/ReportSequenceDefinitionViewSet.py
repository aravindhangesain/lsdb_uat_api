from rest_framework import viewsets
from lsdb.models import ReportSequenceDefinition
from lsdb.serializers import ReportSequenceDefinitionSerializer

class ReportSequenceDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ReportSequenceDefinition.objects.all()
    serializer_class = ReportSequenceDefinition