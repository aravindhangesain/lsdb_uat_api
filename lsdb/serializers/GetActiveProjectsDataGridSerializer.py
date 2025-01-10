from rest_framework import serializers
from lsdb.models import Project,LocationLog,Location

class GetActiveProjectsDataGridSerializer(serializers.HyperlinkedModelSerializer):
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)
    location=serializers.SerializerMethodField()
    location_name=serializers.SerializerMethodField()

    def get_location(self, instance):
        project_id = instance.id
        
        
        latest_location_log = LocationLog.objects.filter(project_id=project_id, is_latest=True).first()
        
        if latest_location_log:
            return latest_location_log.location_id 
        return None 
    
    def get_location_name(self,obj):

        location_id = self.get_location(obj)  # Retrieve the location_id from `get_location`
        if location_id:
            location = Location.objects.filter(id=location_id).first()
            if location:
                return location.name

    class Meta:
        model = Project
        fields = [
            'id',
            'url',
            'sfdc_number',
            'number',
            'project_manager',
            'project_manager_name',
            'customer',
            'customer_name',
            'disposition',
            'disposition_name',
            'group',
            'location',
            'location_name'
        ]

