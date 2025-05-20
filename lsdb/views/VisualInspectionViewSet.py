from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.permissions import ConfiguredPermission
from lsdb.serializers import *
from lsdb.models import *
from rest_framework.response import Response

class VisualInspectionViewSet(LoggingMixin,viewsets.ModelViewSet):
    logging_method = ['POST','PUT','PATCH','DELETE']
    queryset = VisualInspection.objects.all()
    serializer_class = VisualInspectionSerializer
    permission_classes=[ConfiguredPermission]