from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class CheckListViewSet(viewsets.ModelViewSet):
    queryset = CheckList.objects.all()
    serializer = CheckListSerializer