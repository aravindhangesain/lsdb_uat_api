from rest_framework import serializers
from lsdb.models import *

class AssetSubAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetSubAsset
        fields = '__all__'