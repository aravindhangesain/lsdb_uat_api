from rest_framework import serializers
from lsdb.models import ReportTypeDefinition

class ReportTypeDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportTypeDefinition
        fields='__all__'