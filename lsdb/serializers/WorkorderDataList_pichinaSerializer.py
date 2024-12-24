from rest_framework import serializers
from lsdb.models import Workorder_pichina


class WorkorderDataList_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    customer = serializers.ReadOnlyField(source='project.customer.url')
    customer_name = serializers.ReadOnlyField(source='project.customer.name')
    project_number = serializers.ReadOnlyField(source='project.number')
    sfdc_number = serializers.ReadOnlyField(source='project.sfdc_number')

    class Meta:
        model = Workorder_pichina
        fields = [
            'id',
            'name',
            'customer',
            'customer_name',
            'project_number',
            'sfdc_number',
        ]
