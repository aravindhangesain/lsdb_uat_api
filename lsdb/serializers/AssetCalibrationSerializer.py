from rest_framework import serializers
from lsdb.models import AssetCalibration
from datetime import timedelta
from django.utils.timezone import now

class AssetCalibrationSerializer(serializers.HyperlinkedModelSerializer):
    location_name = serializers.ReadOnlyField(source='location.name')
    next_calibration_date = serializers.SerializerMethodField()
    days_since_calibrated = serializers.SerializerMethodField()
    days_to_next_calibration = serializers.SerializerMethodField()

    def get_next_calibration_date(self, obj):
        if obj.last_calibrated_date and obj.schedule_for_calibration:
            return obj.last_calibrated_date + timedelta(days=obj.schedule_for_calibration)
        return None

    def get_days_since_calibrated(self, obj):
        if obj.last_calibrated_date:
            return (now().date() - obj.last_calibrated_date.date()).days
        return None

    def get_days_to_next_calibration(self, obj):
        next_calibration = self.get_next_calibration_date(obj)
        if next_calibration:
            return (next_calibration.date() - now().date()).days
        return None

    class Meta:
        model = AssetCalibration
        fields =[
            'id',
            'asset',
            'asset_number',
            'asset_name',
            'description',
            'last_action_datetime',
            'location',
            'location_name',
            'manufacturer',
            'usage',
            'model',
            'serial_number',
            'is_calibration_required',
            'last_calibrated_date',
            'schedule_for_calibration',
            'next_calibration_date',
            'days_since_calibrated',
            'days_to_next_calibration'
        ]