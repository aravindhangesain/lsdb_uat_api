from rest_framework import serializers
from lsdb.models import ReportFileTemplate

AZURE_BLOB_BASE_URL = "https://haveblueazdev.blob.core.windows.net/reportmedia/"

class ReportFileTemplateSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.file:
            ret['file'] = AZURE_BLOB_BASE_URL + instance.file.name
        else:
            ret['file'] = None
        return ret

    class Meta:
        model = ReportFileTemplate
        fields = [
            'id',
            'file',
            'name',
            'report',
            'workorder',
            'user_id',
            'datetime'
        ]
