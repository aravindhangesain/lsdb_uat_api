from rest_framework import serializers
from lsdb.models import GroupType


class GroupTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = GroupType
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
