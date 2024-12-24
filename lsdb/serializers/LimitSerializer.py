from rest_framework import serializers
from lsdb.models import Limit

class LimitSerializer(serializers.HyperlinkedModelSerializer):
    limit_comparison_one_name = serializers.ReadOnlyField(source='limit_comparison_one.name')
    limit_comparison_two_name = serializers.ReadOnlyField(source='limit_comparison_two.name')
    limit_comparison_mode_name = serializers.ReadOnlyField(source='limit_comparison_mode.name')
    si_prefix_name = serializers.ReadOnlyField(source='si_prefix.name')

    class Meta:
        model = Limit
        fields = [
            'id',
            'url',
            'value_boolean',
            'value_string',
            'limit_one',
            'limit_two',
            'limit_comparison_one',
            'limit_comparison_one_name',
            'limit_comparison_two',
            'limit_comparison_two_name',
            'limit_comparison_mode',
            'limit_comparison_mode_name',
            'precision',
            'units',
            'scientific_format',
            'si_prefix',
            'si_prefix_name',
            'choice_of_list',
            'case_sensitive_compare_string',
        ]
