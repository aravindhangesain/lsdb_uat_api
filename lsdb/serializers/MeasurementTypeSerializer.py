from rest_framework import serializers
from lsdb.models import MeasurementType


class MeasurementTypeSerializer(serializers.HyperlinkedModelSerializer):
    # out_of_family_limit_name = serializers.ReadOnlyField(source='out_of_family_limit.name')
    limit_name = serializers.ReadOnlyField(source='limit.__str__')
    parent_measurement_type_name = serializers.ReadOnlyField(source='parent_measurement_type.name')
    measurement_result_type_name = serializers.ReadOnlyField(source='measurement_result_type.name')

    class Meta:
        model = MeasurementType
        fields = [
            'id',
            'url',
            'name',
            'description',
            'order_by',
            # 'out_of_family_limit',
            # 'out_of_family_limit_name',
            'limit',
            'limit_name',
            'parent_measurement_type',
            'parent_measurement_type_name',
            'measurement_result_type',
            'measurement_result_type_name',
        ]
