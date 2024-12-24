from rest_framework import serializers
from lsdb.models import Disposition_pichina
from lsdb.models import DispositionCode_pichina
from lsdb.serializers import Disposition_pichinaSerializer

class DispositionCodeList_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    dispositions = Disposition_pichinaSerializer(Disposition_pichina.objects.all(), many=True, read_only=True)

    class Meta:
        model = DispositionCode_pichina
        fields = [
            'id',
            'url',
            'name',
            'dispositions',
        ]
