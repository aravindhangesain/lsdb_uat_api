from rest_framework import serializers
from lsdb.models import MeasurementResultType_pichina


class MeasurementResultType_pichinaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MeasurementResultType_pichina
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
