from rest_framework import viewsets
from lsdb.serializers import WorkOrderTemplateSerializer
from lsdb.models import WorkOrderTemplate


class WorkOrderTemplateViewSet(viewsets.ModelViewSet):

    queryset = WorkOrderTemplate.objects.all()
    serializer_class = WorkOrderTemplateSerializer