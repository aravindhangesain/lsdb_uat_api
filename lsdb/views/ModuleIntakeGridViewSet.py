from rest_framework import viewsets
from lsdb.models import ModuleIntakeDetails
from lsdb.serializers import ModuleIntakeGridSerializer

class ModuleIntakeGridViewSet(viewsets.ReadOnlyModelViewSet):
    
    queryset = ModuleIntakeDetails.objects.all()
    serializer_class = ModuleIntakeGridSerializer
    # pagination_class=None