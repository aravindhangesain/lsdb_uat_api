from rest_framework import serializers
from lsdb.models import ModuleTechnology_pichina


class ModuleTechnology_pichinaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ModuleTechnology_pichina
        fields = [
            'id',
            'url',
            'name',
            'description',
            'diode_ideality_factor',
        ]
