from rest_framework import serializers
from lsdb.models import UnitType

class GetModelTypeSerializer(serializers.ModelSerializer):
     class Meta:
        model = UnitType
        fields = [
            'id',
            'model'
        ]