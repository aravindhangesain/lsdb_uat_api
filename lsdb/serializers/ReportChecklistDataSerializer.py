from rest_framework import serializers
from lsdb.models import *

class ReportChecklistDataSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ReportChecklistData
        fields = [
            'id',
            'report',
            'checklist',
            'checklist_report',
            'status',
            'note'
        ]