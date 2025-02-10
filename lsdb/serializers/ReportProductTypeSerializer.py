from rest_framework import serializers
from lsdb.models import ReportProductType

class ReportProductTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportProductType
        fields='__all__'