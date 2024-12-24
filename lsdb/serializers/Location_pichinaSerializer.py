from rest_framework import serializers
from lsdb.models import Location_pichina

class Location_pichinaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Location_pichina
        fields = [
            'id',
            'url',
            'name',
            'description',
            'parent_location',
        ]
