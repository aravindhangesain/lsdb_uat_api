from rest_framework import serializers
from lsdb.models import AzureFile

class FileUploadforFlashSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    procedure_result_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = AzureFile
        fields = [
            'file',
            'procedure_result_id'
        ]