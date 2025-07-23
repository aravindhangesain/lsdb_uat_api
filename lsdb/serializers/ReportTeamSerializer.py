from rest_framework import serializers
from lsdb.models import *

class ReportTeamSerializer(serializers.ModelSerializer):
    writer_name = serializers.ReadOnlyField(source='writer.username')
    approver_name = serializers.ReadOnlyField(source='approver.username')
    reviewer_name = serializers.ReadOnlyField(source='reviewer.username')


    class Meta:
        model = ReportTeam
        fields = [
            'id',
            'url',
            'report_type',
            'reviewer', 
            'writer',
            'writer_name',
            'approver',
            'approver_name',
            'reviewer_name',
            'is_projmanager',
            'obligated_date'
        ]   
        