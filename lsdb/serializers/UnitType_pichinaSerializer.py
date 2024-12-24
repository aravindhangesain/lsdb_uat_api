from rest_framework import serializers
from lsdb.models import UnitType_pichina
from lsdb.serializers.ModuleProperty_pichinaSerializer import ModuleProperty_pichinaSerializer

class UnitType_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    datasheets = serializers.SerializerMethodField()
    module_property = ModuleProperty_pichinaSerializer()
    manufacturer_name = serializers.ReadOnlyField(source='manufacturer.name')
    # unit_type_family_name =serializers.SerializerMethodField()

    def get_datasheets(self,obj):
        return []
    
    class Meta:
        model = UnitType_pichina
        fields = [
            'id',
            'url',
            'model',
            'bom',
            'description',
            'notes',
            'manufacturer',
            'manufacturer_name',
            'datasheets',
            # 'unit_type_family_name',
            'module_property',
        ]
