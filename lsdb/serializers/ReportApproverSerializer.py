from rest_framework import serializers
from lsdb.models import *

class ReportApproverSerializer(serializers.HyperlinkedModelSerializer):
    report_type_name = serializers.ReadOnlyField(source='report_type.name')
    
    class Meta:
        model = ReportApprover
        fields = [
            'id',
            'url',
            'approver_name',
            'report_type',
            'report_type_name'
        ]