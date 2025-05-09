from rest_framework import serializers
from lsdb.models import ScannedPannels,ModuleIntakeDetails,UnitType, WorkOrder,Unit,Location,Disposition
from lsdb.serializers import ModuleIntakeDetailsSerializer, ModulePropertySerializer

class ScannedPannelsSerializer(serializers.ModelSerializer):
    test_sequence_name = serializers.ReadOnlyField(source='test_sequence.name')
    newcrateintake_id=serializers.ReadOnlyField(source='module_intake.newcrateintake.id')
    crate_name=serializers.ReadOnlyField(source='newcrateintake.crate_name')
    location_id=serializers.ReadOnlyField(source='module_intake.location.id')
    unit_type_id=serializers.SerializerMethodField()
    module_type=serializers.ReadOnlyField(source='module_intake.module_type')

    def get_unit_type_id(self, obj):
        try:
            module_type = obj.module_intake.module_type
            unit_type = UnitType.objects.get(model=module_type)
            return unit_type.id
        except UnitType.DoesNotExist:
            return None
        
    class Meta:
        model = ScannedPannels
        fields = [
            'id',
            'serial_number',
            'test_sequence',
            'test_sequence_name',
            'status',
            'module_intake',
            'newcrateintake_id',
            'location_id',
            'module_type',
            'unit_type_id',
            'crate_name'
            ]
        
class ModuleInventorySerializer(serializers.ModelSerializer):
    project_number=serializers.ReadOnlyField(source='module_intake.projects.number')
    workorder_name=serializers.ReadOnlyField(source='module_intake.bom')
    workorder_id=serializers.SerializerMethodField()
    eol_disposition=serializers.SerializerMethodField()
    # eol_disposition_name=serializers.ReadOnlyField(source='eol_disposition.name')
    eol_disposition_name = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    location_id=serializers.SerializerMethodField()
    module_specification=serializers.SerializerMethodField()
    work_order_id=serializers.SerializerMethodField()
    ntp_date=serializers.SerializerMethodField()
    customer_name=serializers.ReadOnlyField(source='module_intake.customer.name')
    module_type = serializers.ReadOnlyField(source='module_intake.module_type')
    test_sequence_name=serializers.ReadOnlyField(source='test_sequence.name')
    intake_location=serializers.ReadOnlyField(source='module_intake.location.name')
    arrival_date=serializers.ReadOnlyField(source='module_intake.received_date')
    




    def get_location_id(self, instance):
        serialnumber = instance.serial_number
        unit = Unit.objects.filter(serial_number=serialnumber).first()
        if unit and unit.location_id:
            location = Location.objects.filter(id=unit.location_id).first()
            if location:
                return location.id
        return "NA"
    
    

    

    def get_location(self, instance):
        serialnumber = instance.serial_number
        unit = Unit.objects.filter(serial_number=serialnumber).first()
        if unit and unit.location_id:
            location = Location.objects.filter(id=unit.location_id).first()
            if location:
                return location.name
        return "NA"
    
    def get_workorder_id(self, obj):
        workorder = WorkOrder.objects.filter(
            name=obj.module_intake.bom,
            project_id=obj.module_intake.projects_id
        ).first()  # Use .first() to get the first match or None if no match
        if workorder:
            return workorder.id
        return None  # Handle the case where no matching WorkOrder is found
    
    def get_eol_disposition_name(self, obj):
        if obj.eol_disposition:
            return obj.eol_disposition.name
        return None
    
    def get_eol_disposition(self, obj):
        if obj.eol_disposition:
            return obj.eol_disposition.id
        return None
    
    def get_module_specification(self, obj):
        try:
            unit_type = UnitType.objects.get(model=obj.module_intake.module_type)
            module_property = unit_type.module_property
            return ModulePropertySerializer(module_property, context=self.context).data if module_property else {}
        except Exception as message:
            return {}
        
    def get_work_order_id(self, obj):
        workorder = WorkOrder.objects.filter(
            name=obj.module_intake.bom,
            project_id=obj.module_intake.projects_id
        ).first()  # Use .first() to get the first match or None if no match

        if workorder:
            return workorder.id
        return None  # Handle the case where no matching WorkOrder is found
    

    def get_ntp_date(self, obj):
        workorder = WorkOrder.objects.filter(
            name=obj.module_intake.bom,
            project_id=obj.module_intake.projects_id
        ).first()  # Use .first() to get the first match or None if no match

        if workorder:
            return workorder.start_datetime
        return None
    
    class Meta:
        model= ScannedPannels
        fields = [
            'id',
            'serial_number',
            'location_id',
            'location',
            'module_intake',
            'customer_name',
            'project_number',
            'workorder_name',
            'workorder_id',
            'arrival_date',
            'project_closeout_date',
            'eol_disposition',
            'eol_disposition_name',
            'module_specification',
            'work_order_id',
            'ntp_date',
            'module_type',
            'test_sequence',
            'test_sequence_name',
            'intake_location'
        ]

class ModuleIntakeSerializer(serializers.ModelSerializer):
    customer_name=serializers.ReadOnlyField(source='customer.name')
    intake_location_name=serializers.ReadOnlyField(source='location.name')
    class Meta:
        model = ModuleIntakeDetails
        fields = ['id','location','intake_location_name','lot_id','customer','bom','module_type','number_of_modules','steps','is_complete','intake_date','received_date','intake_by','newcrateintake','customer_name']

class ModuleInventoryDetailSerializer(serializers.ModelSerializer):
    project_number = serializers.ReadOnlyField(source='module_intake.projects.number')
    workorder_name = serializers.ReadOnlyField(source='module_intake.bom')
    workorder_id = serializers.SerializerMethodField()
    module_intake = ModuleIntakeSerializer(read_only=True)  # Nested serializer for module_intake
    module_data = ModuleIntakeDetailsSerializer(many=True, read_only=True)  # Nested serializer for module_data
    module_type = serializers.ReadOnlyField(source='module_intake.module_type')
    module_specification = serializers.SerializerMethodField()
    eol_disposition_name = serializers.SerializerMethodField()
    location=serializers.SerializerMethodField()
    location_name=serializers.SerializerMethodField()
    test_sequence_name=serializers.ReadOnlyField(source='test_sequence.name')
    ntp_date=serializers.SerializerMethodField()

    def get_location(self, instance):
        serialnumber = instance.serial_number
        unit = Unit.objects.filter(serial_number=serialnumber).first()
        if unit and unit.location_id:
            return unit.location_id
        else:
            return "NA"
        
    def get_location_name(self, instance):
        serialnumber = instance.serial_number
        unit = Unit.objects.filter(serial_number=serialnumber).first()
        if unit and unit.location_id:
            location = Location.objects.filter(id=unit.location_id).first()
            if location:
                return location.name
        return "NA"
    
    def get_module_specification(self, obj):
        try:
            unit_type = UnitType.objects.get(model=obj.module_intake.module_type)
            module_property = unit_type.module_property
            return ModulePropertySerializer(module_property, context=self.context).data if module_property else {}
        except Exception as message:
            return {}
        
    def get_eol_disposition_name(self, obj):
        if obj.eol_disposition:
            return obj.eol_disposition.name
        return None
    
    def get_workorder_id(self, obj):
        workorder = WorkOrder.objects.filter(
            name=obj.module_intake.bom,
            project_id=obj.module_intake.projects_id
        ).first()  # Use .first() to get the first match or None if no match

        if workorder:
            return workorder.id
        return None  # Handle the case where no matching WorkOrder is found
    

    def get_ntp_date(self, obj):
        workorder = WorkOrder.objects.filter(
            name=obj.module_intake.bom,
            project_id=obj.module_intake.projects_id
        ).first()  # Use .first() to get the first match or None if no match

        if workorder:
            return workorder.start_datetime
        return None  # Handle the case where no matching WorkOrder is found
    
    class Meta:
        model = ScannedPannels
        fields = [
            'id',
            'serial_number',
            'location',
            'location_name',
            'module_intake',
            'project_number',
            'workorder_name',
            'workorder_id',
            'arrival_date',
            'project_closeout_date',
            'module_data',
            'eol_disposition',
            'eol_disposition_name',
            'module_specification',
            'module_type',
            'ntp_date',
            'test_sequence',
            'test_sequence_name'
        ]









