from rest_framework import serializers
from lsdb.models import ReportSequenceDefinition

class ReportSequenceDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    disposition_name=serializers.ReadOnlyField(source='disposition.name')
    class Meta:
        model=ReportSequenceDefinition
        fields=[
            'id',
            'url',
            'name',
            'short_name',
            'description',
            'disposition',
            'disposition_name',
            'version',
            'created_date',
            'hex_color',

        ]