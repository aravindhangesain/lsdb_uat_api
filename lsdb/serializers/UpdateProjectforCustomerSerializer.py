from rest_framework import serializers
from lsdb.models import Project,LocationLog


class UpdateProjectforCustomerSerializer(serializers.HyperlinkedModelSerializer):
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)
    location=serializers.SerializerMethodField()


    def get_location(self, instance):
        project_id = instance.id
        latest_location_log = LocationLog.objects.filter(project_id=project_id, is_latest=True).first()
        if latest_location_log:
            return latest_location_log.location_id 
        return None 

    class Meta:
        model = Project
        fields = [
            'id',
            'url',
            'number',
            'sfdc_number',
            'project_manager',
            'project_manager_name',
            'disposition',
            'disposition_name',
            'proposal_price',
            'location',
        ]