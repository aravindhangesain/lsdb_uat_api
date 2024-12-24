from rest_framework import serializers
from lsdb.models import UnitTypePropertyDataType

class UnitTypePropertyDataTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UnitTypePropertyDataType
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
