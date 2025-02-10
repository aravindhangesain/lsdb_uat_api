from rest_framework import serializers
from lsdb.models import ReportSequenceDefinition

class ReportSequenceDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportSequenceDefinition
        fields='__all__'