from rest_framework import viewsets
from lsdb.models import Asset, AssetCalibration
from lsdb.serializers import AssetCalibrationSerializer

class AssetCalibrationViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCalibration.objects.all()
    serializer_class = AssetCalibrationSerializer

    def perform_create(self, serializer):
        asset_calibration = serializer.save()
        asset_data = {
            "name": asset_calibration.asset_name,
            "description": asset_calibration.description,
            "location_id":asset_calibration.location.id,
            "last_action_datetime": asset_calibration.last_action_datetime,
            "disposition_id":16
        }
        Asset.objects.create(**asset_data)
