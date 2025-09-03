from rest_framework import serializers
from lsdb.models import *
from datetime import datetime


class AssetSubAssetSerializer(serializers.ModelSerializer):

    asset_name = serializers.ReadOnlyField(source='asset.name', read_only=True)
    sub_asset_name = serializers.ReadOnlyField(source='sub_asset.sub_asset_name', read_only=True)
    last_calibrated_date = serializers.ReadOnlyField(source='sub_asset.last_calibrated_date', read_only=True)
    next_calibration = serializers.ReadOnlyField(source='sub_asset.next_calibration', read_only=True)
    days_to_next_calibration = serializers.SerializerMethodField()
    is_valid_subasset = serializers.SerializerMethodField()

    def get_days_to_next_calibration(self, obj):
        sub_asset_id=obj.sub_asset.id

        sub_asset=SubAsset.objects.get(id=sub_asset_id)
        if sub_asset.last_calibrated_date and sub_asset.next_calibration is not None:
            delta = datetime.now(sub_asset.last_calibrated_date.tzinfo) - sub_asset.last_calibrated_date
            days_passed = delta.days
            days_remaining = sub_asset.next_calibration - days_passed
            return days_remaining if days_remaining >= 0 else 0
        return None
    
    def get_is_valid_subasset(self, obj):

        days_to_next_calibration = self.get_days_to_next_calibration(obj)
        if days_to_next_calibration<1:
            return False
        else:
            return True


    class Meta:
        model = AssetSubAsset
        fields = [
            'id',
            'asset_id',
            'asset_name',
            'sub_asset_id',
            'sub_asset_name',
            'days_to_next_calibration',
            'last_calibrated_date',
            'next_calibration',
            'is_valid_subasset'
        ]