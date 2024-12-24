from rest_framework import serializers
from lsdb.models import ModuleIntakeDetails, WorkOrder
from datetime import datetime

class ModuleIntakeDetailsSerializer(serializers.ModelSerializer):
    intake_by = serializers.CharField(read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name')
    manufacturer_name = serializers.ReadOnlyField(source='customer.name')
    crate_name = serializers.ReadOnlyField(source='newcrateintake.crate_name')
    project_number = serializers.ReadOnlyField(source='projects.number')
    ntp_date = serializers.SerializerMethodField()

    def get_ntp_date(self,obj):
        workorder = WorkOrder.objects.filter(name=obj.bom,project_id = obj.projects.id).first()
        if workorder:
            return workorder.start_datetime
        else:
            return None

    class Meta:
        model = ModuleIntakeDetails
        fields = [
            'id',
            'location',
            'lot_id',
            'projects',
            'project_number',
            'customer',
            'customer_name',
            'manufacturer_name',
            'bom',
            'module_type',
            'number_of_modules',
            'is_complete',
            'steps',
            'intake_date',
            'received_date',
            'intake_by',
            'newcrateintake',
            'crate_name',
            'ntp_date',
        ]

    def create(self, validated_data):
        request = self.context.get('request', None)
        user = request.user if request else None
        intake_by = user.username if user else None
        validated_data['intake_by'] = intake_by
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        request = self.context.get('request', None)
        user = request.user if request else None
        instance.intake_by = user.username if user else None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance









