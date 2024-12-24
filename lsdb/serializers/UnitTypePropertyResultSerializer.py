from rest_framework import serializers
from lsdb.models import UnitTypePropertyResult

class UnitTypePropertyResultSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UnitTypePropertyResult
        fields = [
            'id',
            'url',
            'unit_type',
            'unit_type_property_type',
            'value_double',
            'value_datetime',
            'value_string',
            'value_boolean',
        ]
