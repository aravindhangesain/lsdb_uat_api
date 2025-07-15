from rest_framework import serializers
from lsdb.models import ReportReviewer

class ReportReviewerSerializer(serializers.HyperlinkedModelSerializer):
    report_type_name = serializers.ReadOnlyField(source='report_type.name')
    
    class Meta:
        model = ReportReviewer
        fields = [
            'id',
            'url',
            'reviewer_name',
            'report_type',
            'report_type_name'
        ]