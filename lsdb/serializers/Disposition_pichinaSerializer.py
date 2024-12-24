from rest_framework import serializers
from lsdb.models import Disposition_pichina

class Disposition_pichinaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Disposition_pichina
        fields = [
            'id',
            'url',
            'name',
            'complete',
            'description',
        ]


