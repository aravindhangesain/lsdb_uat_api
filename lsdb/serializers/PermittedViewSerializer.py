from rest_framework import serializers
from lsdb.models import PermittedView


class PermittedViewSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PermittedView
        fields = [
            'id',
            'url',
            'name'
        ]
