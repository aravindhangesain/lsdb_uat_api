from rest_framework import viewsets

from lsdb.serializers import UnitTypeTemplateSerializer
from lsdb.models import UnitTypeTemplate

class UnitTypeTemplateViewSet(viewsets.ModelViewSet):

    queryset=UnitTypeTemplate.objects.all()
    serializer_class=UnitTypeTemplateSerializer