from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import DispositionCodeSerializer
from lsdb.models import DispositionCode
from lsdb.permissions import ConfiguredPermission


class DispositionCodeViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows DispositionCode to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = DispositionCode.objects.all()
    serializer_class = DispositionCodeSerializer
    permission_classes = [ConfiguredPermission]
