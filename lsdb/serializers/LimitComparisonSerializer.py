from rest_framework import serializers
from lsdb.models import LimitComparison

class LimitComparisonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = LimitComparison
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
