from rest_framework import serializers
from lsdb.models import ReportResult


class ReportResultSerilaizer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ReportResult
        fields='__all__'