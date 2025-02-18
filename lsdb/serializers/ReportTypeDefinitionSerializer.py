from rest_framework import serializers
from lsdb.models import ReportTypeDefinition

class ReportTypeDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportTypeDefinition
        fields=[
            'id',
            'url',
            'name',
            'disposition',
            'group',
            'version',
            'linear_execution_order'
        ]