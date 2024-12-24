from rest_framework import serializers
from lsdb.models import TestSequenceDefinition_pichina

class TestSequenceDefinition_pichinaSerializer(serializers.ModelSerializer):
    disposition_name = serializers.ReadOnlyField(source='disposition.name')

    class Meta:
        model = TestSequenceDefinition_pichina
        fields = [
            'id',
            'url',
            'name',
            'short_name',
            'description',
            'notes',
            'disposition',
            'disposition_name',
            'version',
            'group',
            # 'unit_type_family',
            'hex_color',
        ]
