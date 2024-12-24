from rest_framework import serializers
from lsdb.models import UnitType,ExpectedUnitType
from lsdb.serializers.ModulePropertySerializer import ModulePropertySerializer

class GetModuleDetailsSerializer(serializers.ModelSerializer):
    module_property = ModulePropertySerializer()
    expected_unit_count = serializers.SerializerMethodField()

    def get_expected_unit_count(self, obj):
        # Extract the ID of the current model instance
        model_id = obj.id
        # Use this ID to get all corresponding expected counts from the ExpectedUnitType table
        expected_unit_types = ExpectedUnitType.objects.filter(unit_type_id=model_id)
        if expected_unit_types.exists():
            # Sum all the expected counts
            total_expected_count = sum(eut.expected_count for eut in expected_unit_types)
            return total_expected_count
        else:
            return None  # or any default value if no expected counts are found
        
    class Meta:
        model = UnitType
        fields = [
            'id',
            'model',
            'module_property',
            'expected_unit_count'
        ]