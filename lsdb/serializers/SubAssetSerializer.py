from rest_framework import serializers
from lsdb.models import *
from datetime import datetime

class SubAssetSerializer(serializers.ModelSerializer):

    days_to_next_calibration = serializers.SerializerMethodField()
    is_valid_subasset=serializers.SerializerMethodField()

    def get_days_to_next_calibration(self, obj):
        if obj.last_calibrated_date and obj.next_calibration is not None:
            delta = datetime.now(obj.last_calibrated_date.tzinfo) - obj.last_calibrated_date
            days_passed = delta.days
            days_remaining = obj.next_calibration - days_passed
            return days_remaining if days_remaining >= 0 else 0
        return None
    
    def get_is_valid_subasset(self, obj):

        days_to_next_calibration = self.get_days_to_next_calibration(obj)
        if days_to_next_calibration<1:
            return False
        else:
            return True
        
    class Meta:
        model = SubAsset
        fields = ['id', 'name', 'description', 'last_calibrated_date','next_calibration','days_to_next_calibration','is_valid_subasset']