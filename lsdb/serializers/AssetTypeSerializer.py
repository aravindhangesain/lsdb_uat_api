from rest_framework import serializers
from lsdb.models import AssetType
from lsdb.models import Asset

from lsdb.serializers import AssetSerializer

class AssetTypeSerializer(serializers.HyperlinkedModelSerializer):
    assets = serializers.SerializerMethodField()

    def get_assets(self, obj):
        return AssetSerializer(obj.asset_set.all(), many=True, context=self.context).data

    class Meta:
        model = AssetType
        fields = [
            'id',
            'url',
            'name',
            'description',
            'assets',
        ]
        read_only_fields = [
            'assets',
        ]
