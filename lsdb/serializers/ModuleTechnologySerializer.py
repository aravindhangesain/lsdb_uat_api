from rest_framework import serializers
from lsdb.models import ModuleTechnology


class ModuleTechnologySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ModuleTechnology
        fields = [
            'id',
            'url',
            'name',
            'description',
            'diode_ideality_factor',
        ]
