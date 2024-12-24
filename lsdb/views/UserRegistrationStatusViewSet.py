from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import UserRegistrationStatusSerializer
from lsdb.models import UserRegistrationStatus
from lsdb.permissions import ConfiguredPermission


class UserRegistrationStatusViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows UserRegistrationStatus to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UserRegistrationStatus.objects.all()
    serializer_class = UserRegistrationStatusSerializer
    permission_classes = [ConfiguredPermission]
