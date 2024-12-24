from rest_framework import serializers
from lsdb.models import LimitComparisonMode

class LimitComparisonModeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = LimitComparisonMode
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
