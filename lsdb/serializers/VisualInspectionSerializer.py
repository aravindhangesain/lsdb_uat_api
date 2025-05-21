from rest_framework import serializers
from lsdb.models import *

class VisualInspectionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=VisualInspection
        fields=[
            'id',
            'url',
            'procedure_result',
            'procedure_definition',
            'calibration_date',
            'ambient_temperature',
            'humidity',
        ]