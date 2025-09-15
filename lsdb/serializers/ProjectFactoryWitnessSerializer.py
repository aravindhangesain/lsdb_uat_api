from rest_framework import serializers
from lsdb.models import *
from lsdb.serializers import *

class ProjectFactoryWitnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFactoryWitness
        fields = '__all__'