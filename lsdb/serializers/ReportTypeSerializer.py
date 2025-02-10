from rest_framework import serializers
from lsdb.models import ReportType

class ReportTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportType
        fields='__all__'