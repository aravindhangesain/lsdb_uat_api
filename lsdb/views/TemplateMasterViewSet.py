from rest_framework import viewsets
from lsdb.models import TemplateMaster
from lsdb.serializers import TemplateMasterSerializer

class TemplateMasterViewSet(viewsets.ModelViewSet):

    queryset = TemplateMaster.objects.all()
    serializer_class = TemplateMasterSerializer
