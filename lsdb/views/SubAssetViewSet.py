from rest_framework import viewsets
from lsdb.serializers import *
from lsdb.models import *

class SubAssetViewSet(viewsets.ModelViewSet):
    queryset = SubAsset.objects.all()
    serializer_class = SubAssetSerializer
  