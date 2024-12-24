from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import PropertySerializer
from lsdb.models import Property
from lsdb.permissions import ConfiguredPermission


class PropertyViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Property to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [ConfiguredPermission]
