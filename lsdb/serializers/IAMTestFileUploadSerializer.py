from rest_framework import serializers
from lsdb.models import IAMTestFileUpload

class IAMTestFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = IAMTestFileUpload
        fields = [
            'id',
            'file_path',
            'serial_number',
            'uploaded_date'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        azure_container = 'testmedia1'
        azure_blob_url = f"https://haveblueazdev.blob.core.windows.net/{azure_container}/{instance.file_path}"
        representation['file_path'] = azure_blob_url
        return representation     
