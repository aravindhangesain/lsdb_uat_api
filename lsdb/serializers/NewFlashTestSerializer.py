from rest_framework import serializers
from lsdb.models import *
import random
from lsdb.serializers import *


class NewFlashTestSerializer(serializers.ModelSerializer):
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    module_property = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')

    def get_module_property(self, obj):
        unit_type_id = Unit.objects.filter(id=obj.unit.id).values_list('unit_type_id', flat=True).first()
        module_property_id = UnitType.objects.filter(id=unit_type_id).values_list('module_property_id', flat=True).first()
        if module_property_id:
            module_property = ModuleProperty.objects.get(id=module_property_id)
            desired_fields = ['id', 'number_of_cells', 'nameplate_pmax','module_width','module_height','system_voltage','module_technology_name','isc','voc','imp','vmp','alpha_isc','beta_voc','gamma_pmp','cells_in_series','cells_in_parallel','cell_area','bifacial']
            module_property_serializer = ModulePropertySerializer(module_property, context=self.context)
            full_data = module_property_serializer.data
            filtered_data = {field: full_data[field] for field in desired_fields if field in full_data}
            return filtered_data
        return None

    def get_filename(self, obj):
        test_generated_number = random.randint(10000, 99999)
        serial_number = Unit.objects.filter(id=obj.unit.id).values_list('serial_number', flat=True).first()
        unit_type_id = Unit.objects.filter(id=obj.unit.id).values_list('unit_type_id', flat=True).first()
        module_property_id = UnitType.objects.filter(id=unit_type_id).values_list('module_property_id', flat=True).first()
        isc = ModuleProperty.objects.filter(id=module_property_id).values_list('isc', flat=True).first()
        if isc is not None:
            isc_str = str(isc)
            if '.' in isc_str:
                isc = isc_str.replace('.', '_') 
        return f"DSC_{test_generated_number}_{serial_number}_{isc}A_1s"
    
    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'unit',
            'serial_number',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'module_property',
            'filename',
            'name',
            'procedure_definition',
            'procedure_definition_name',
            'disposition'
        ]
