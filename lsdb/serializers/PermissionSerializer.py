from rest_framework import serializers
from lsdb.models import Permission


class PermissionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Permission
        fields = [
            'id',
            'url',
            'name',
            'group',
            'permission_types',
            'permitted_views',
        ]
