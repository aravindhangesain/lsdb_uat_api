from rest_framework import serializers
from lsdb.models import *

class CheckListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckList
        fields = [
            'id',
            'category',
            'check_point'
        ]
