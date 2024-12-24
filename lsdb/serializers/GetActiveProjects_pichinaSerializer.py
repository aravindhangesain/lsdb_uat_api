from rest_framework import serializers
from lsdb.models import Project_pichina

class GetActiveProjects_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    # project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)

    
    class Meta:
        model = Project_pichina
        fields = [
            'id',
            'url',
            'sfdc_number',
            'number',
            'customer',
            'customer_name',
            'disposition',
            'disposition_name',
        ]

