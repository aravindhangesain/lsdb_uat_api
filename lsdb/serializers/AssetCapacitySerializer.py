from rest_framework import serializers
from lsdb.models import AssetCapacity


class AssetCapacitySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AssetCapacity
        fields = [
            'id',
            'url',
            'serial_number',
            'project_id',
            'work_order_name',
            # 'asset',
        ]
