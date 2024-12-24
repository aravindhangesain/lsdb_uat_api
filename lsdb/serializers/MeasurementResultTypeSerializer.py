from rest_framework import serializers
from lsdb.models import MeasurementResultType


class MeasurementResultTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MeasurementResultType
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
