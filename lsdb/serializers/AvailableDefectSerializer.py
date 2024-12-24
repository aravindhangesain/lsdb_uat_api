from rest_framework import serializers
from lsdb.models import AvailableDefect


class AvailableDefectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AvailableDefect
        fields = [
            'id',
            'url',
            'category',
            'short_name',
            'description',
        ]
