from rest_framework import serializers
from lsdb.models import NewCrateIntake


class NewCrateIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewCrateIntake
        fields = [
            'id',
            'customer',
            'manufacturer',
            'crate_intake_date',
            'project',
            'created_by',
            'created_on',
            'crate_name'
            ]                                                                                                                                                            