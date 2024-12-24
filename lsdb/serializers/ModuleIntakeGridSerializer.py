from rest_framework import serializers
from lsdb.models import ModuleIntakeDetails
from datetime import datetime

class ModuleIntakeGridSerializer(serializers.ModelSerializer):
    customer_name= serializers.SerializerMethodField()
    manufacturer_name = serializers.SerializerMethodField()
    

    def get_manufacturer_name(self, obj):
        return obj.customer.name if obj.customer else None
    
    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else None
    
    class Meta:
        model = ModuleIntakeDetails
        fields = [
            'location',
            'lot_id',
            'projects',
            'customer',
            'customer_name',
            'bom',
            'module_type',
            'number_of_modules',
            'is_complete',
            'intake_date',
            'received_date',
            'intake_by',
            'manufacturer_name',
            ]
