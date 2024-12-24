from rest_framework import serializers
from lsdb.models import MeasurementDefinition


class MeasurementDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    measurement_result_type_field = serializers.ReadOnlyField(source='measurement_result_type.name')

    class Meta:
        model = MeasurementDefinition
        fields = [
            'id',
            'url',
            'name',
            'limit',
            'record_only',
            'allow_skip',
            'requires_review',
            'step_definition',
            'condition_definition',
            'measurement_type',
            # 'measurement_definition',
            # 'apply_out_of_family_limit',
            'order',
            'report_order',
            'measurement_result_type',
            'measurement_result_type_field',
        ]
