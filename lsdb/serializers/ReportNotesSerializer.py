from rest_framework import serializers
from lsdb.models import ReportNotes

class ReportNotesSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    reviewer_name = serializers.ReadOnlyField(source='reviewer.reviewer.username')


    class Meta:
        model = ReportNotes
        fields = [
            'id',
            'url',
            'report',
            'subject',
            'comment',
            'type',
            'user',
            'user_name',
            'datetime',
            'reviewer',
            'reviewer_name'
        ]
        