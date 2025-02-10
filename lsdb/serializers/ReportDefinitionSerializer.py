from rest_framework import serializers
from lsdb.models import ReportDefinition

class ReportDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportDefinition
        fields='__all__'