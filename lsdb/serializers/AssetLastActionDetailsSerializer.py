from rest_framework import serializers
from lsdb.models import *

class AssetLastActionDetailsSerializer(serializers.HyperlinkedModelSerializer):

    asset_name=serializers.ReadOnlyField(source='asset.asset_number',read_only=True)
    username=serializers.ReadOnlyField(source='user.username',read_only=True)

    class Meta:
        model=AssetLastActionDetails
        fields=[
            'id',
            'asset',
            'asset_id',
            'asset_name',
            'action_name',
            'action_datetime',
            'user',
            'user_id',
            'username'
        ]