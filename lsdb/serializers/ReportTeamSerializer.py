from rest_framework import serializers
from lsdb.models import *

class ReportTeamSerializer(serializers.ModelSerializer):
    writer_name = serializers.ReadOnlyField(source='writer.username')
    approver_name = serializers.ReadOnlyField(source='approver.username')
    reviewer_name = serializers.ReadOnlyField(source='reviewer.username')
    report_name = serializers.ReadOnlyField(source='report_type.name')


    class Meta:
        model = ReportTeam
        fields = [
            'id',
            'url',
            'report_type',
            'report_name',
            'reviewer', 
            'writer',
            'writer_name',
            'approver',
            'approver_name',
            'reviewer_name',
            'is_projmanager',
            'duration',
            'reviewer_pm'
        ]   
        