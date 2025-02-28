from rest_framework import serializers
from lsdb.models import AssetCalibration

class AssetCalibrationSerializer(serializers.HyperlinkedModelSerializer):
    location_name = serializers.ReadOnlyField(source='location.name')

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