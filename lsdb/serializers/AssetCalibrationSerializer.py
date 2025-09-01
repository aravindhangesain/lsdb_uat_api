from rest_framework import serializers
from lsdb.models import AssetCalibration
from datetime import timedelta
from django.utils.timezone import now

class AssetCalibrationSerializer(serializers.HyperlinkedModelSerializer):
    location_name = serializers.ReadOnlyField(source='location.name')
    asset_type_name = serializers.ReadOnlyField(source='asset_type.name')
    next_calibration_date = serializers.SerializerMethodField()
    days_since_calibrated = serializers.SerializerMethodField()
    days_to_next_calibration = serializers.SerializerMethodField()
    azurefile_download=serializers.SerializerMethodField()
    calibration_days = serializers.SerializerMethodField()
    
    def get_calibration_days(self, obj):
        if obj.last_calibrated_date:
            delta = now().date() - obj.last_calibrated_date.date()
            return delta.days
        return None


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
    
    def get_azurefile_download(self, obj):
        azurefile_id=obj.azurefile_id
        if azurefile_id==None:
            return None
        azurefile_download="https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/"+str(azurefile_id)+"/download"
        return azurefile_download
    


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
            'days_to_next_calibration',
            'asset_type',
            'asset_type_name',
            'external_asset_required',
            'azurefile',
            'azurefile_id',
            'azurefile_download',
            'calibration_days',
        ]