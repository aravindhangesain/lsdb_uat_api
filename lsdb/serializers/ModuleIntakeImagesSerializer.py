from rest_framework import serializers
from lsdb.models import ModuleIntakeImages


class ModuleIntakeImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleIntakeImages
        fields = [
            'id', 
            'moduleintake', 
            'label_name', 
            'image_path', 
            'status',
            'notes'
        ]     

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        azure_container = 'testmedia1'
        azure_blob_url = f"https://haveblueazdev.blob.core.windows.net/{azure_container}/{instance.image_path}"
        representation['image_path'] = azure_blob_url
        return representation  