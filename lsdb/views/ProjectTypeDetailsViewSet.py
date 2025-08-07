from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class ProjectTypeDetailsViewSet(viewsets.ModelViewSet):
    queryset = ProjectTypeDetails.objects.all()
    serializer_class = ProjectTypeDetailsSerializer