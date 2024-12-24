
from django.contrib.auth.models import User
from rest_framework import viewsets
from lsdb.models import StepResult_pichina

from lsdb.serializers import StepResult_pichinaSerializer
from lsdb.permissions import ConfiguredPermission


class StepResult_pichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows StepResult to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepResult_pichina.objects.all()
    serializer_class = StepResult_pichinaSerializer
    permission_classes = [ConfiguredPermission]

    