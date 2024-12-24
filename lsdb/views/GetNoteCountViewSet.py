from lsdb.models import Project
from lsdb.serializers import GetNoteCountSerializer
from rest_framework import viewsets
from lsdb.permissions import ConfiguredPermission

class GetNoteCountViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Project to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Project.objects.filter(disposition__complete=False)
    serializer_class = GetNoteCountSerializer
    permission_classes = [ConfiguredPermission]
    pagination_class = None