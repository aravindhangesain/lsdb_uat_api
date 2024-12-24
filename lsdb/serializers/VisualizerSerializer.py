from rest_framework import serializers
from lsdb.models import Visualizer

# This code is a stub, it does nothing
class VisualizerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Visualizer
        fields = [
            'id',
            'url',
            'name',
            'description',
        ]
