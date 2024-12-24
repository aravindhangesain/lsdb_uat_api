from rest_framework import serializers
from lsdb.models import DispositionCode

class DispositionCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DispositionCode
        fields = [
            'id',
            'url',
            'name',
            'dispositions',
        ]
