from rest_framework import serializers
from lsdb.utils.HasHistory_pichina import unit_history
from lsdb.models import Unit_pichina


class Unit_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    history = serializers.SerializerMethodField()
    model = serializers.ReadOnlyField(source='unit_type.model')
    bom = serializers.ReadOnlyField(source='unit_type.bom')
    disposition_name  = serializers.ReadOnlyField(source='disposition.name')

    def get_history(self, obj):
        return (unit_history(obj))


    class Meta:
        model = Unit_pichina
        fields = [
            'id',
            'url',
            'unit_type',
            'fixture_location',
            # 'crate',
            'intake_date',
            'serial_number',
            'disposition',
            'disposition_name',
            'tib',
            'location',
            'name',
            'model',
            'bom',
            'description',
            # 'notes',
            'history',
            # 'project_set',
            # 'unit_images',
            # 'workorder_set',
        ]