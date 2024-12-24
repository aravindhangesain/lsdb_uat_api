from rest_framework import serializers
from lsdb.models import AvailableDefect, AvailableDefect_pichina


class AvailableDefect_pichinaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AvailableDefect_pichina
        fields = [
            'id',
            'url',
            'category',
            'short_name',
            'description',
        ]
