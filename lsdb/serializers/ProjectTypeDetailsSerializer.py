from rest_framework import serializers
from lsdb.models import *

class ProjectTypeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTypeDetails
        fields = [
            'id',
            'name'
        ]
        