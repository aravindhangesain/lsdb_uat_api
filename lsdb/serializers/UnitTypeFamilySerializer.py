from rest_framework import serializers
from lsdb.models import UnitTypeFamily

class UnitTypeFamilySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UnitTypeFamily
        fields = [
            'id',
            'url',
            'name',
            'description',
            'measurement_types',
        ]
