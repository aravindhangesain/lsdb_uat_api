from rest_framework import serializers
from lsdb.models import ModuleIntake


class ModuleIntakeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ModuleIntake
        fields= '__all__'
