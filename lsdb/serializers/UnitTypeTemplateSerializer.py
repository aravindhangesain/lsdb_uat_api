from rest_framework import serializers
from lsdb.models import UnitTypeTemplate

class UnitTypeTemplateSerializer(serializers.HyperlinkedModelSerializer):
    unittype_id=serializers.ReadOnlyField(source='unittype.id')

    class Meta:
        model=UnitTypeTemplate
        fields=[
            'id',
            'name',
            'url',
            'unittype_id',
            'unittype'
        ]