from rest_framework import serializers
from lsdb.models import StepType_pichina

class StepType_pichinaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StepType_pichina
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
