from rest_framework import serializers
from lsdb.models import *

class ReportChecklistNoteSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = ReportChecklistNote
        fields = [
            'id',
            'report',
            'checklist',
            'checklist_report',
            'subject',
            'comment',
            'user',
            'username',
            'datetime'           
        ]