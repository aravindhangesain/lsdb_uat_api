from rest_framework import serializers
from lsdb.models import Label

class LabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Label
        fields = [
            'id',
            'url',
            'name',
            'description',
            'hex_color',
        ]
