from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class AssetLastActionDetailsViewSet(viewsets.ModelViewSet):
    queryset=AssetLastActionDetails.objects.all()
    serializer_class=AssetLastActionDetailsSerializer