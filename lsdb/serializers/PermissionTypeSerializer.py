from rest_framework import serializers
from lsdb.models import PermissionType


class PermissionTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PermissionType
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
