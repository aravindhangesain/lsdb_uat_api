from rest_framework import serializers
from lsdb.models import Customer_pichina,Project_pichina


class Customer_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    project_numbers = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    def get_notes(self,request):
        return []

    def get_project_numbers(self, obj):
        customer_id = obj.id  # Assuming `obj` has `customer_id`
        projects = Project_pichina.objects.filter(customer_id=customer_id).values("id", "number")
        return list(projects)

    class Meta:
        model = Customer_pichina
        fields = [
            'id',
            'url',
            'name',
            'short_name',
            'project_numbers',
            'notes',
            'is_pvel',
        ]
