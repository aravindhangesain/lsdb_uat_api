from rest_framework import serializers
from lsdb.models import ProcedureResult,Unit,UnitType,ModuleProperty,TestSequenceDefinition
import random
from lsdb.serializers import ModulePropertySerializer


class IVandEL_InProgressSerializer(serializers.ModelSerializer):
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
            
            module_property_serializer = ModulePropertySerializer(module_property, context=self.context)
            
            return module_property_serializer.data 

        return None

    def get_filename(self, obj):
        test_generated_number = random.randint(10000, 99999)
        
        # Retrieve serial_number as a single value
        serial_number = Unit.objects.filter(id=obj.unit.id).values_list('serial_number', flat=True).first()

        # Retrieve unit_type_id and module_property_id as single values
        unit_type_id = Unit.objects.filter(id=obj.unit.id).values_list('unit_type_id', flat=True).first()
        module_property_id = UnitType.objects.filter(id=unit_type_id).values_list('module_property_id', flat=True).first()

        # Retrieve isc as a single value
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
