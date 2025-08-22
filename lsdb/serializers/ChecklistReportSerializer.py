from rest_framework import serializers
from lsdb.models import *
from lsdb.serializers import *
from collections import defaultdict

class ChecklistReportSerializer(serializers.ModelSerializer):
    checklist = serializers.SerializerMethodField()

    def get_checklist(self, obj):
        sections = defaultdict(list)
        for cl in obj.checklist.all():
            sections[cl.category].append({
                "id": cl.id,
                "description": cl.check_point
            })
        result = []
        for category, checkpoints in sections.items():
            result.append({
                "category": category,
                "check_point": checkpoints
            })
        return result

    class Meta:
        model = ChecklistReport
        fields = [
            'id',
            'report_name',
            'checklist'
        ]