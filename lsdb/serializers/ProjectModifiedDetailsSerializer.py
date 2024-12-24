from django.utils import timezone
from rest_framework import serializers
from lsdb.models import ProjectModifiedDetails


class ProjectModifiedDetailsSerializer(serializers.HyperlinkedModelSerializer):
    modified_by = serializers.ReadOnlyField(source='modified_by.username', read_only=True)
    modified_on = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()


    def get_role(self, obj):
        return "superuser" if obj.modified_by and obj.modified_by.is_superuser else "staff"

    def get_modified_on(self, instance):
        if self.context['request'].method == 'POST':
            return timezone.now().date()
        else:
            # If it's not a POST request, return the existing value from the model
            return instance.modified_on  # Assuming 'modified_on' is a field in ProjectModifiedDetails

 
    class Meta:
        model = ProjectModifiedDetails
        fields = [
            'id',
            'modified_by',
            'modified_on',
            'role',
            'number',
            'comments',
        ]
    
    