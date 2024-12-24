from rest_framework import serializers
from lsdb.models import UnitType
from lsdb.models import AzureFile
from lsdb.serializers import AzureFileSerializer

class UnitTypeListSerializer(serializers.HyperlinkedModelSerializer):
    datasheets = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)

    class Meta:
        model = UnitType
        fields = [
            'id',
            'url',
            'model',
            'bom',
            'description',
            'notes',
            'manufacturer',
            'measurement_types',
            'datasheets',
            'unit_type_family',
            'module_property',
        ]
        read_only_fields = [
            'datasheets',
        ]
