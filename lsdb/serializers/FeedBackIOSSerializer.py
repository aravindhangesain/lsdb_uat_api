from rest_framework import serializers
from lsdb.models import FeedBackIOS

class FeedBackIOSSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField() 
    username = serializers.SerializerMethodField() 
    # fb_files = serializers.ListField(child=serializers.FileField(),write_only=True,required=False)
    
    class Meta:
        model = FeedBackIOS
        fields = ['id','files','username','comments','fb_type','priority','created_at','user']
        read_only_fields = ['user', 'created_at']

    def get_files(self, obj):
        data = []
     
        for fb_files in obj.feedback_files.all():
            azure_id = fb_files.azurefile.id
            filename = fb_files.azurefile.name
            data.append({
                "file_id": azure_id,
                "download_url": f"https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/{azure_id}/download",
                "filename":filename
            })

        return data
    
    def get_username(self,obj):
        return obj.user.username

    
