from rest_framework import serializers
from lsdb.models import ModuleProperty_pichina


class ModuleProperty_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    module_technology_name = serializers.ReadOnlyField(source='module_technology.name')

    class Meta:
        model = ModuleProperty_pichina
        fields = [
            'id',
            'number_of_cells',
            'nameplate_pmax',
            'module_width',
            'module_height',
            'system_voltage',
            'module_technology',
            'module_technology_name',
            'auditor',
            'audit_date',
            'audit_report_id',
            'isc',
            'voc',
            'imp',
            'vmp',
            'alpha_isc',
            'beta_voc',
            'gamma_pmp',
            'cells_in_series',
            'cells_in_parallel',
            'cell_area',
            'bifacial',
        ]
