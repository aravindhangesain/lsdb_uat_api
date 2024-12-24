from rest_framework import serializers
from lsdb.models import Disposition
from lsdb.models import DispositionCode
from lsdb.serializers import DispositionSerializer

class DispositionCodeListSerializer(serializers.HyperlinkedModelSerializer):
    dispositions = DispositionSerializer(Disposition.objects.all(), many=True, read_only=True)

    class Meta:
        model = DispositionCode
        fields = [
            'id',
            'url',
            'name',
            'dispositions',
        ]
