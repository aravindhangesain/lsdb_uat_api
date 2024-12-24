# This serializer is obsolete and is left here for historical reference only
from rest_framework import serializers
from lsdb.models import OutOfFamilyLimit


class OutOfFamilyLimitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = OutOfFamilyLimit
        fields = [
            'id',
            'url',
            'limit_one',
            'limit_two',
        ]
