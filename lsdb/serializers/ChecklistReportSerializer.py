from rest_framework import serializers
from lsdb.models import *

class ChecklistReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistReport
        fields = '__all__'