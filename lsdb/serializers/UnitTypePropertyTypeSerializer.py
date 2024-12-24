from rest_framework import serializers
from lsdb.models import UnitTypePropertyType

class UnitTypePropertyTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UnitTypePropertyType
        fields = [
            'id',
            'url',
            'name',
            'value',
            'source',
            'description',
            'tag',
            'controlled',
            'group',
        ]
