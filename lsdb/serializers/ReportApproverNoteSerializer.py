from rest_framework import serializers
from lsdb.models import *

class ReportApproverNoteSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    approver_name = serializers.ReadOnlyField(source='approver.approver.username')
    
    class Meta:
        model = ReportApproverNote
        fields = [
            'id',
            'report',
            'subject',
            'comment',
            'type',
            'user',
            'username',
            'datetime',
            'approver',
            'approver_name'

        ]