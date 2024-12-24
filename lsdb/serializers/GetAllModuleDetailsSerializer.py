from rest_framework import serializers
from lsdb.models import ModuleIntakeImages, ModuleIntakeDetails, ScannedPannels, UnitType, ExpectedUnitType
from lsdb.serializers import ModulePropertySerializer  # Assuming this is the correct path

class GetAllModuleDetailsSerializer(serializers.ModelSerializer):
    module_intake_details = serializers.SerializerMethodField()
    scanned_pannel_details = serializers.SerializerMethodField()
    module_image_details = serializers.SerializerMethodField()
    module_property_details = serializers.SerializerMethodField()
    expected_unit_count = serializers.SerializerMethodField()
    BASE_URL = 'https://haveblueazdev.blob.core.windows.net/testmedia1/'

    def get_module_intake_details(self, obj):
        return {
            'moduleintake_id': obj.moduleintake_id,
            'location': obj.moduleintake.location_id,
            'location_name': 'NAPA',
            'lot_id': obj.moduleintake.lot_id,
            'projects_id': obj.moduleintake.projects_id,
            'project_number': obj.moduleintake.projects.number,
            'customer': obj.moduleintake.customer_id,
            'customer_name': obj.moduleintake.customer.name,
            'manufacturer_name': obj.moduleintake.customer.name,
            'bom': obj.moduleintake.bom,
            'number_of_modules': obj.moduleintake.number_of_modules,
            'steps': obj.moduleintake.steps,
            'is_complete': obj.moduleintake.is_complete,
            'intake_date': obj.moduleintake.intake_date,
            'received_date':obj.moduleintake.received_date,
            'intake_by': obj.moduleintake.intake_by,
            'newcrateintake': obj.moduleintake.newcrateintake_id,
            'crate_name':obj.moduleintake.newcrateintake.crate_name
        }
    
    def get_scanned_pannel_details(self, obj):
        scannedpannels = ScannedPannels.objects.filter(module_intake_id=obj.moduleintake_id)
        return [
            {
                'id': panel.id,
                'serial_number': panel.serial_number,
                'test_sequence': panel.test_sequence.id,
                'test_sequence_name':panel.test_sequence.name,
                'module_type': obj.moduleintake.module_type,
                'status': panel.status
            }
            for panel in scannedpannels
        ]
    
    def get_module_image_details(self, obj):
        return [
            {
                'id': obj.id,
                'label_name': obj.label_name,
                'image_path': f"{self.BASE_URL}/{obj.image_path}" if obj.image_path else None
            }
        ]
    
    def get_module_property_details(self, obj):
        try:
            unit_type = UnitType.objects.get(model=obj.moduleintake.module_type)
            module_property = unit_type.module_property
            return ModulePropertySerializer(module_property, context=self.context).data if module_property else {}
        except UnitType.DoesNotExist:
            return {}
        
    def get_expected_unit_count(self, obj):
        try:
            unit_type = UnitType.objects.get(model=obj.moduleintake.module_type)
            expected_unit_type = ExpectedUnitType.objects.filter(unit_type_id=unit_type.id).first()
            return [expected_unit_type.expected_count] if expected_unit_type else []
        except UnitType.DoesNotExist:
            return {}
        
    class Meta:
        model = ModuleIntakeImages
        fields = [
            'module_intake_details',
            'scanned_pannel_details',
            'module_image_details',
            'module_property_details',
            'expected_unit_count',
        ]









