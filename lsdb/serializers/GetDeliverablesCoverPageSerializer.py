from rest_framework import serializers
from lsdb.models import DeliverablesCoverData
class GetDeliverablesCoverPageSerializer(serializers.HyperlinkedModelSerializer):
    project_number = serializers.ReadOnlyField(source='project.number')
    customer_name = serializers.ReadOnlyField(source='customer.name')
    workorder_name = serializers.ReadOnlyField(source='workorder.name')
    author_name = serializers.ReadOnlyField(source='author.username')
    checked_by_name = serializers.ReadOnlyField(source='checked.username')
    approved_by_name = serializers.ReadOnlyField(source='approved.username')
    class Meta:
        model = DeliverablesCoverData
        fields = [
            'id',
            'url',
            'title',
            'customer',
            'customer_name',
            'contact_name',
            'contact_email',
            'project',
            'project_number',
            'workorder',
            'workorder_name',
            'revision',
            'status',
            'date',
            'classification',
            'author',
            'author_name',
            'checked',
            'checked_by_name',
            'approved',
            'approved_by_name',
            'provided_by'
        ]
        extra_kwargs = {
            'url': {'lookup_field': 'workorder_id'}
        }
