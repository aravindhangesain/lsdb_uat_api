from rest_framework import serializers
from lsdb.models import *

class VisualInspectionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=VisualInspection
        fields=[
            'procedure_result',
            'procedure_definition',
            'calibration_date',
            'ambient_temperature',
            'ambient_humidity',
        ]