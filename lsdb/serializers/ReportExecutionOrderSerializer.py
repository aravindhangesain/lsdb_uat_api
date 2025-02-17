from rest_framework import serializers
from lsdb.models import ReportExecutionOrder

class ReportExecutionOrderSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportExecutionOrder
        fields='__all__'