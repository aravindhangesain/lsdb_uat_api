from rest_framework import viewsets
from lsdb.models import WorkOrder
from lsdb.serializers import GetDeliverablesCoverPageSerializer

class GetDeliverablesCoverPageViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = GetDeliverablesCoverPageSerializer
    lookup_field = 'id' 
