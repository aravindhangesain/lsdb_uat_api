from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import OrganizationSerializer
from lsdb.models import Organization
from lsdb.permissions import ConfiguredPermission


class OrganizationViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Organization to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [ConfiguredPermission]
