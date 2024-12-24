from rest_framework import serializers
from lsdb.models import Property


class PropertySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Property
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
