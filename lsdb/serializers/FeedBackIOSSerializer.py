from rest_framework import serializers
from lsdb.models import FeedBackIOS

class FeedBackIOSSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()  
    # fb_files = serializers.ListField(child=serializers.FileField(),write_only=True,required=False)
    
    class Meta:
        model = FeedBackIOS
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def get_files(self, obj):
        data = []
     
        for fb_files in obj.feedback_files.all():
            azure_id = fb_files.azurefile.id
            data.append({
                "file_id": azure_id,
                "download_url": f"https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/{azure_id}/download"
            })

        return data