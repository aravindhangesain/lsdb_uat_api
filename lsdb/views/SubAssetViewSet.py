from datetime import datetime
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from lsdb.models import AssetCalibration
from lsdb.serializers import SubAssetSerializer


class SubAssetViewSet(viewsets.ModelViewSet):
    queryset = AssetCalibration.objects.all()  # or SubAsset if that’s correct
    serializer_class = SubAssetSerializer
    lookup_field = 'asset_number'

    def retrieve(self, request, *args, **kwargs):
        asset_number = self.kwargs.get(self.lookup_field)
        if not asset_number:
            raise NotFound(detail="asset_number query parameter is required")

        try:
            sub_asset = AssetCalibration.objects.get(asset_number=asset_number)
        except AssetCalibration.DoesNotExist:
            raise NotFound(detail="Asset not found")

        def get_days_to_next_calibration(obj):
            if obj.last_calibrated_date and obj.schedule_for_calibration is not None:
                now = datetime.now(obj.last_calibrated_date.tzinfo)
                delta = now - obj.last_calibrated_date
                days_passed = delta.days
                days_remaining = obj.schedule_for_calibration - days_passed
                return max(days_remaining, 0)
            return None

        def get_is_valid_subasset(obj):
            days_to_next = get_days_to_next_calibration(obj)
            return days_to_next is not None and days_to_next >= 1

        return Response({
            'sub_asset_id': sub_asset.id,
            'sub_asset_name': sub_asset.asset_name,
            'asset_number': sub_asset.asset_number,
            'description': sub_asset.description,
            'last_calibrated_date': sub_asset.last_calibrated_date,
            'next_calibration': sub_asset.schedule_for_calibration,
            'days_to_next_calibration': get_days_to_next_calibration(sub_asset),
            'is_valid_subasset': get_is_valid_subasset(sub_asset),
            'disposition_id': sub_asset.disposition.id
        })
