from rest_framework import viewsets 
from lsdb.models import *
from lsdb.serializers import *

class RevokedAssetDetailsViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCalibration.objects.filter(disposition_id = 14)
    serializer_class = AssetCalibrationSerializer
    # pagination_class = None