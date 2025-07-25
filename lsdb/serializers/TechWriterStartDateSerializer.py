from rest_framework import serializers
from lsdb.models import *


class TechWriterStartDateSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = ReportWriterAgenda
        fields = [
            'id',
            'report_result',
            'tech_writer_start_date',
            'user',
            'username'
        ]