from rest_framework import viewsets
from lsdb.serializers import *
from lsdb.models import *


class StressRunResultViewSet(viewsets.ModelViewSet):
    queryset = StressRunResult.objects.all()
    serializer_class = StressRunResultSerializer