from rest_framework import viewsets
from lsdb.models import DeliverablesCoverData
from lsdb.serializers import GetDeliverablesCoverPageSerializer

class GetDeliverablesCoverPageViewSet(viewsets.ModelViewSet):
    queryset = DeliverablesCoverData.objects.all()
    serializer_class = GetDeliverablesCoverPageSerializer
    lookup_field = 'workorder_id'

    def get_queryset(self):
        workorder_id = self.kwargs.get('workorder_id')
        if workorder_id:
            return DeliverablesCoverData.objects.filter(workorder_id=workorder_id)
        return DeliverablesCoverData.objects.all()
