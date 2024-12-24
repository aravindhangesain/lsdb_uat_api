from rest_framework import viewsets
from lsdb.serializers import Disposition_pichinaSerializer
from lsdb.models import Disposition_pichina
from lsdb.permissions import ConfiguredPermission



class Disposition_PichinaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Dispositions to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Disposition_pichina.objects.all()
    serializer_class = Disposition_pichinaSerializer
    permission_classes = [ConfiguredPermission]
