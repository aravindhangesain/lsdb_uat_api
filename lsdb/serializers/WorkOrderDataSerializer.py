from rest_framework import serializers

from lsdb.models import WorkOrder,LocationLog,Location

class WorkOrderDataListSerializer(serializers.HyperlinkedModelSerializer):
    customer = serializers.ReadOnlyField(source='project.customer.url')
    customer_name = serializers.ReadOnlyField(source='project.customer.name')
    project_number = serializers.ReadOnlyField(source='project.number')
    sfdc_number = serializers.ReadOnlyField(source='project.sfdc_number')
    project_manager_name = serializers.ReadOnlyField(source='project.project_manager.username')
    location=serializers.SerializerMethodField()
    location_name=serializers.SerializerMethodField()

    def get_location(self,obj):
        project_id=obj.project_id
        latest_location_log = LocationLog.objects.filter(project_id=project_id, is_latest=True).first()
        
        if latest_location_log:
            return latest_location_log.location_id 
        return None

    def get_location_name(self,obj):

        project_id=obj.project_id
        
        latest_location_log = LocationLog.objects.filter(project_id=project_id, is_latest=True).first()
        
        if latest_location_log:
            
            location_id= latest_location_log.location_id
            
            
            location = Location.objects.filter(id=location_id).first()
            
            print(location.name)
            return location.name
            
        else:
            return None
                
                    
                    
                
            
            


        
        

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'name',
            'customer',
            'customer_name',
            'project_number',
            'sfdc_number',
            'project_manager_name',
            'location',
            'location_name'
        ]

#If I need this:
class WorkOrderDataDetailSerializer(serializers.HyperlinkedModelSerializer):
    customer = serializers.ReadOnlyField(source='project.customer')
    customer_name = serializers.ReadOnlyField(source='project.customer.name')
    project_number = serializers.ReadOnlyField(source='project.number')
    sfdc_number = serializers.ReadOnlyField(source='project.sfdc_number')
    project_manager_name = serializers.ReadOnlyField(source='project.project_manager.username')

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'name',
            'customer',
            'customer_name',
            'project_number',
            'sfdc_number',
            'project_manager_name',
        ]
