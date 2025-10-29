from rest_framework import serializers
from lsdb.models import *

class RetestReasonsSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = RetestReasons
        fields = [
            'id',
            'url',
            'reason',
            'description',
        ]