from rest_framework import serializers
from lsdb.models import FeedBackIOS

class FeedBackIOSSerializer(serializers.HyperlinkedModelSerializer):
    fb_file = serializers.FileField()
    fb_file_id = serializers.ReadOnlyField(source='fb_file.id')
    azurefile_download=serializers.SerializerMethodField()

    class Meta:
        model = FeedBackIOS
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    
    def get_azurefile_download(self, obj):
        azurefile_id=obj.fb_file_id
        if azurefile_id==None:
            return None
        azurefile_download="https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/"+str(azurefile_id)+"/download"
        return azurefile_download