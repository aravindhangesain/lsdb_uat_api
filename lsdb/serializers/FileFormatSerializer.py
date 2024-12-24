from rest_framework import serializers
from lsdb.models import FileFormat

class FileFormatSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = FileFormat
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
