from rest_framework import serializers
from lsdb.models import CrateIntakeImages


class CrateIntakeImagesSerializer(serializers.ModelSerializer):

    crate_name=serializers.ReadOnlyField(source='newcrateintake.crate_name')
    class Meta:
        model = CrateIntakeImages
        fields = [
            'id', 
            'newcrateintake', 
            'label_name', 
            'image_path', 
            'uploaded_date', 
            'project', 
            'status',
            'notes',
            'crate_name'
        ]      

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        azure_container = 'testmedia1'
        azure_blob_url = f"https://haveblueazdev.blob.core.windows.net/{azure_container}/{instance.image_path}"
        representation['image_path'] = azure_blob_url
        return representation 
                                                                                                                                                           