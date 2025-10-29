from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class RetestReasonsViewSet(viewsets.ModelViewSet):
    queryset = RetestReasons.objects.all()
    serializer_class = RetestReasonsSerializer