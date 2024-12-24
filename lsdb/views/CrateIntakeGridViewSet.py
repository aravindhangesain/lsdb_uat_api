from rest_framework import viewsets
from lsdb.models import NewCrateIntake
from lsdb.serializers import CrateIntakeGridSerializer

class CrateIntakeGridViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = NewCrateIntake.objects.all()
    serializer_class = CrateIntakeGridSerializer
    pagination_class = None

