from rest_framework import serializers
from lsdb.models import *
from lsdb.serializers import *

class ProjectdownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 
            'number', 
        ]