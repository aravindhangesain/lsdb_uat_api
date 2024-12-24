from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import UserProfileSerializer
from lsdb.models import UserProfile
from lsdb.permissions import ConfiguredPermission


class UserProfileViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows UserProfile to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [ConfiguredPermission]
