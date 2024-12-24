from rest_framework import serializers
from lsdb.models import NewCrateIntake

class CrateIntakeGridSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    manufacturer_name = serializers.ReadOnlyField(source='customer.name')
    project_number = serializers.ReadOnlyField(source='project.number')

    class Meta:
        model = NewCrateIntake
        fields = [
            'id',
            'customer',
            'customer_name',
            'manufacturer',
            'manufacturer_name',
            'crate_intake_date',
            'project',
            'project_number',
            'created_by',
            'created_on',
            'crate_name'
        ]