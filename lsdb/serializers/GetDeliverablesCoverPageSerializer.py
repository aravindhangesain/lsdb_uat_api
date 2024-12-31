from rest_framework import serializers
from lsdb.models import WorkOrder

class GetDeliverablesCoverPageSerializer(serializers.ModelSerializer):
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    project_number = serializers.ReadOnlyField(source='project.number')
    unit_disposition_name = serializers.ReadOnlyField(source='unit_disposition.name')
    customer_name = serializers.ReadOnlyField(source='project.customer.name')
    contact_name = serializers.ReadOnlyField(source='project.customer.contact_name')
    contact_email = serializers.ReadOnlyField(source='project.customer.contact_email')
    author = serializers.ReadOnlyField(source='project.project_manager.username')
    checked = serializers.ReadOnlyField(source='project.project_manager.username')
    approved_by = serializers.ReadOnlyField(source='project.project_manager.username')

    class Meta:
        model = WorkOrder
        fields = [
            'id',
            'url',
            'name',
            'description',
            'project',
            'project_number',
            'start_datetime', # NTP Date
            'disposition',
            'disposition_name',
            'unit_disposition',
            'unit_disposition_name',
            'customer_name',
            'contact_name',
            'contact_email',
            'author',
            'checked',
            'approved_by',
            'tib',
        ]
