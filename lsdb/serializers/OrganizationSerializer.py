from rest_framework import serializers
from lsdb.models import Organization


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Organization
        fields = [
            'id',
            'url',
            'name',
        ]
