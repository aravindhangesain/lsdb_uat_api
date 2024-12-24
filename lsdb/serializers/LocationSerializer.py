from rest_framework import serializers
from lsdb.models import Location

class LocationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Location
        fields = [
            'id',
            'url',
            'name',
            'description',
            'parent_location',
        ]
