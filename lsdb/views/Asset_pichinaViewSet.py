from rest_framework import viewsets
from lsdb.models import Asset_pichina
from lsdb.serializers import Asset_pichinaSerializer
from lsdb.permissions import ConfiguredPermission


class Asset_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Asset_pichina.objects.all()
    serializer_class = Asset_pichinaSerializer
    permission_classes = [ConfiguredPermission]

    