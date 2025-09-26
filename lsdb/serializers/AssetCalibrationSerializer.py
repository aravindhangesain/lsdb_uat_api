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
    is_calibration = serializers.SerializerMethodField()
    is_calibration_date = serializers.SerializerMethodField()
    in_use = serializers.SerializerMethodField()
    
    def get_calibration_days(self, obj):
        if obj.last_calibrated_date:
            delta = now().date() - obj.last_calibrated_date.date()
            return delta.days
        return None
    
    def get_is_calibration(self, obj):
        next_calibration = self.get_next_calibration_date(obj)
        if next_calibration:
            days = (next_calibration.date() - now().date()).days
            if days <= 0:
                return False
            return True
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
            return abs((next_calibration.date() - now().date()).days)
        return None
    
    def get_is_calibration_date(self, obj):
        is_next_calibration = self.get_days_to_next_calibration(obj)
        if is_next_calibration is None:
            return 0
        if is_next_calibration <= 30:
            return True
        return False
    
    def get_in_use(self, obj):
        disposition = obj.disposition.id 
        if disposition in [7]:
            return True
        return False
    
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
            'in_use',
            'is_calibration_required',
            'last_calibrated_date',
            'schedule_for_calibration',
            'next_calibration_date',
            'days_since_calibrated',
            'days_to_next_calibration',
            'is_calibration_date',
            'asset_type',
            'asset_type_name',
            'external_asset_required',
            'azurefile',
            'azurefile_id',
            'azurefile_download',
            'calibration_days',
            'is_calibration',
            'is_main_asset',
            'is_sub_asset',
            'is_rack',
            'disposition',
            'disposition_id',
        ]