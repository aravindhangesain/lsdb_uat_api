from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class ReportTeamViewSet(viewsets.ModelViewSet):
    queryset = ReportTeam.objects.all()
    serializer_class = ReportTeamSerializer