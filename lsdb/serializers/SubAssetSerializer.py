from rest_framework import serializers
from lsdb.models import *

class SubAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubAsset
        fields = '__all__'