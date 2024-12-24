from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import LabelSerializer
from lsdb.models import Label
from lsdb.permissions import ConfiguredPermission


class LabelViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Labels to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [ConfiguredPermission]
