from rest_framework import viewsets
from lsdb.models import NewCrateIntake
from lsdb.serializers import GetAllCrateDetailsSerializer


class GetAllCrateDetailsViewSet(viewsets.ModelViewSet):
    queryset= NewCrateIntake.objects.all()
    serializer_class = GetAllCrateDetailsSerializer
    lookup_field = 'id'

    
