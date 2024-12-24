from rest_framework import serializers

from lsdb.models import WorkOrder

class WorkOrderDataListSerializer(serializers.HyperlinkedModelSerializer):
    customer = serializers.ReadOnlyField(source='project.customer.url')
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
