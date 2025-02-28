from rest_framework import viewsets
from lsdb.models import AssetCalibration
from lsdb.serializers import AssetCalibrationSerializer

class AssetCalibrationViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCalibration.objects.all()
    serializer_class = AssetCalibrationSerializer
