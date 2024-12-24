from rest_framework import serializers
from lsdb.models import MeasurementCorrectionFactor

class MeasurementCorrectionFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model=MeasurementCorrectionFactor
        fields = [
            'id',
            'new_procedure_result_id',
            'old_procedure_result_id',
        ]
