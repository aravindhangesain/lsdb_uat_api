from rest_framework import serializers
from lsdb.models import SiPrefix

class SiPrefixSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = SiPrefix
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
