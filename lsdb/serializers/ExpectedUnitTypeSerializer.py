from rest_framework import serializers
from lsdb.models import ExpectedUnitType

from lsdb.serializers import UnitListSerializer


class ExpectedUnitTypeSerializer(serializers.HyperlinkedModelSerializer):
    manufacturer = serializers.ReadOnlyField(source='unit_type.manufacturer.name', read_only=True)
    model = serializers.ReadOnlyField(source='unit_type.model', read_only=True)
    bom = serializers.ReadOnlyField(source='unit_type.bom', read_only=True)
    project_number = serializers.ReadOnlyField(source='project.number', read_only=True)
    start_date = serializers.ReadOnlyField(source='project.start_date', read_only=True)

    units = serializers.SerializerMethodField()

    def get_units(self, obj):
        units = obj.project.units.filter(unit_type=obj.unit_type)
        # Need to fix this syntax:
        return UnitListSerializer.UnitListSerializer(units, many=True, context=self.context).data

    class Meta:
        model = ExpectedUnitType
        fields = [
            'id',
            'url',
            'expected_count',
            'received_count',
            'project',
            'project_number',
            'start_date',
            'unit_type',
            'manufacturer',
            'model',
            'bom',
            'units',
        ]
