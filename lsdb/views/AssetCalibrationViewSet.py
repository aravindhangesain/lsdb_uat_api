from rest_framework import viewsets
from lsdb.models import Asset, AssetCalibration
from lsdb.serializers import AssetCalibrationSerializer
from django.db import connection
from rest_framework.response import Response
from rest_framework.decorators import action

class AssetCalibrationViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCalibration.objects.all()
    serializer_class = AssetCalibrationSerializer

    def perform_create(self, serializer):
        asset_calibration = serializer.save()
        asset = Asset.objects.create(
            name = asset_calibration.asset_name,
            description = asset_calibration.description,
            location_id = asset_calibration.location.id,
            last_action_datetime = asset_calibration.last_action_datetime,
            disposition_id = 16
        )
        asset_calibration.asset = asset 
        asset_calibration.save(update_fields=['asset'])
        if asset_calibration.asset_type:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO lsdb_asset_asset_types (asset_id, assettype_id) VALUES (%s, %s)",
                    [asset.id, asset_calibration.asset_type.id]
                )

    @action(detail=False, methods=['post','get'])
    def asset_info(self, request):
        asset_id = request.data.get('asset_id')
        if not asset_id:
            return Response({"error": "Asset ID is required"}, status=400)

        try:
            asset_calibration = AssetCalibration.objects.get(asset_id=asset_id)
            serializer = self.get_serializer(asset_calibration)
            data = serializer.data
            return Response({
                "last_calibrated_date": data["last_calibrated_date"],
                "next_calibration_date": data["next_calibration_date"],
                "days_to_next_calibration": data["days_to_next_calibration"]
            }, status=200)

        except AssetCalibration.DoesNotExist:
            return Response({"error": "Asset Calibration not found"}, status=404)