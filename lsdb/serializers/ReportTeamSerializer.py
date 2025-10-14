from rest_framework import serializers
from lsdb.models import *

class ReportTeamSerializer(serializers.ModelSerializer):
    writer_name = serializers.ReadOnlyField(source='writer.username')
    approver_name = serializers.SerializerMethodField()
    reviewer_name = serializers.SerializerMethodField()
    report_name= serializers.ReadOnlyField(source='report_type.name')

    def get_reviewer_name(self, obj):
        try:
            if obj.reviewer and getattr(obj.reviewer, 'username', None):
                return obj.reviewer.username
        except Exception:
            return None

        if getattr(obj, 'reviewer_pm', False):
            return 'PM'
        return None
    
    def get_approver_name(self,obj):

        try:
            if obj.approver and getattr(obj.approver, 'username', None):
                return obj.approver.username
        except Exception:
            return None

        if getattr(obj, 'is_projmanager', False):
            return 'PM'
        return None

    class Meta:
        model = ReportTeam
        fields = [
            'id',
            'url',
            'report_type',
            'report_name',
            'reviewer', 
            'reviewer_name',
            'reviewer_pm',
            'writer',
            'writer_name',
            'approver',
            'approver_name',
            'is_projmanager',
            'duration'
        ]   