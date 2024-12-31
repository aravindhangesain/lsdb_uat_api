from rest_framework import serializers
from lsdb.models import ModuleIntakeDetails
from datetime import datetime

class ModuleIntakeGridSerializer(serializers.ModelSerializer):
    customer_name= serializers.ReadOnlyField(source='customer.name')
    manufacturer_name = serializers.ReadOnlyField(source='customer.name')

    
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
