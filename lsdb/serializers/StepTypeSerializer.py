from rest_framework import serializers
from lsdb.models import StepType

class StepTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = StepType
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
