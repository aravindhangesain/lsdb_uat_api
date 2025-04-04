from rest_framework import serializers
from lsdb.models import HailTest

class HailTestSerializer(serializers.HyperlinkedModelSerializer):
    serial_number = serializers.ReadOnlyField(source='unit.serial_number')

    class Meta:
        model = HailTest
        fields = [
            'id',
            'url',
            'location',
            'date_time',
            'operator',
            'customer_id',
            'project_id',
            'workorder_id',
            'test_sequence_id',
            'character_point_procedure',
            'unit',
            'serial_number',
            'mass_of_hail',
            'flex_tip_mass',
            'diameter',
            'target_speed',
            'measured_speed',
            'units_chosen_for_speed_suggested_pressure',
            'target_pressure',
            'actual_pressure',
            'speed_in_range',
            'module_angle',
            'energy',
            'time',
            'result_comments'
        ]
