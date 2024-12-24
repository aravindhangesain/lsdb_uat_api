from rest_framework import serializers

from lsdb.models import Customer_pichina, Project_pichina
from lsdb.serializers.ProjectList_pichinaSerializer import ProjectList_pichinaSerializer

class CustomerDetail_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    project_set = serializers.SerializerMethodField()

    def get_project_set(self, obj):
        projects = Project_pichina.objects.filter(customer_id=obj.id)
        return ProjectList_pichinaSerializer(projects, many=True, context=self.context).data

    class Meta:
        model = Customer_pichina
        fields = [
            'id',
            'url',
            'name',
            'short_name',
            'project_set',
            'contact_name',
            'contact_email',
            'accounting_email',
            'po_required',
        ]
