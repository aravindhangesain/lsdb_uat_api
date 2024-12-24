from rest_framework import serializers
from lsdb.models import Disposition

class DispositionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Disposition
        fields = [
            'id',
            'url',
            'name',
            'complete',
            'description',
        ]
