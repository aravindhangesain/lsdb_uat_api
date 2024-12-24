from rest_framework import serializers

from lsdb.models import UnitType
from lsdb.models import AzureFile
from lsdb.models import ModuleProperty

from lsdb.serializers.AzureFileSerializer import AzureFileSerializer
from lsdb.serializers.ModulePropertySerializer import ModulePropertySerializer

class UnitTypeSerializer(serializers.HyperlinkedModelSerializer):
    datasheets = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    manufacturer_name = serializers.ReadOnlyField(source='manufacturer.name')
    module_property = ModulePropertySerializer()
    unit_type_family_name =serializers.ReadOnlyField(source='unit_type_family.name')

    class Meta:
        model = UnitType
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
            'unit_type_family',
            'unit_type_family_name',
            'module_property',
        ]
        read_only_fields = [
            'datasheets',
        ]

    def create(self, validated_data):
        property_data = validated_data.pop('module_property')
        property = ModuleProperty.objects.create(**property_data)
        unit_type = UnitType.objects.create(module_property=property,**validated_data)
        return unit_type

    def update(self, instance, validated_data):
        prop_data = validated_data.pop('module_property')
        prop = instance.module_property
        instance.model = validated_data.get('model',instance.model)
        instance.bom = validated_data.get('bom',instance.bom)
        instance.description = validated_data.get('description',instance.description)
        instance.notes = validated_data.get('notes',instance.notes)
        instance.manufacturer = validated_data.get('manufacturer',instance.manufacturer)
        instance.unit_type_family = validated_data.get('unit_type_family',instance.unit_type_family)
        instance.save()

        prop.number_of_cells = prop_data.get('number_of_cells',prop.number_of_cells)
        prop.nameplate_pmax = prop_data.get('nameplate_pmax',prop.nameplate_pmax)
        prop.module_width = prop_data.get('module_width',prop.module_width)
        prop.module_height = prop_data.get('module_height',prop.module_height)
        prop.system_voltage = prop_data.get('system_voltage',prop.system_voltage)
        prop.module_technology = prop_data.get('module_technology',prop.module_technology)
        prop.auditor = prop_data.get('auditor',prop.auditor)
        prop.audit_date = prop_data.get('audit_date',prop.audit_date)
        prop.audit_report_id = prop_data.get('audit_report_id',prop.audit_report_id)
        prop.isc = prop_data.get('isc',prop.isc)
        prop.voc = prop_data.get('voc',prop.voc)
        prop.imp = prop_data.get('imp',prop.imp)
        prop.vmp = prop_data.get('vmp',prop.vmp)
        prop.alpha_isc = prop_data.get('alpha_isc',prop.alpha_isc)
        prop.beta_voc = prop_data.get('beta_voc',prop.beta_voc)
        prop.gamma_pmp = prop_data.get('gamma_pmp',prop.gamma_pmp)
        prop.cells_in_series = prop_data.get('cells_in_series',prop.cells_in_series)
        prop.cells_in_parallel = prop_data.get('cells_in_parallel',prop.cells_in_parallel)
        prop.cell_area = prop_data.get('cell_area',prop.cell_area)
        prop.bifacial = prop_data.get('bifacial',prop.bifacial)
        prop.save()


        return instance
