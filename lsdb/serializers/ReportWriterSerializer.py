from rest_framework import serializers
from lsdb.models import ReportWriter

class ReportWriterSerializer(serializers.HyperlinkedModelSerializer):
    report_type_name = serializers.ReadOnlyField(source='report_type.name')
    
    class Meta:
        model = ReportWriter
        fields = [
            'id',
            'url',
            'writer_name',
            'report_type',
            'report_type_name'
        ]