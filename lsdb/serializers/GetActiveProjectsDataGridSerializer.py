from rest_framework import serializers
from lsdb.models import Project

class GetActiveProjectsDataGridSerializer(serializers.HyperlinkedModelSerializer):
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)

    
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
        ]

