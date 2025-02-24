from rest_framework import serializers
from lsdb.models import ReportExecutionOrder

class ReportExecutionOrderSerializer(serializers.HyperlinkedModelSerializer):
    report_definition_name=serializers.ReadOnlyField(source='report_definition.name')
    product_definition_name=serializers.ReadOnlyField(source='product_definition.name')
    report_sequence_definition_name=serializers.ReadOnlyField(source='report_sequence_definition.name')

    class Meta:
        model=ReportExecutionOrder
        fields=[
            'id',
            'url',
            'execution_group_name',
            'report_definition_id',
            'report_definition',
            'report_definition_name',

            'product_definition_id',
            'product_definition',
            'product_definition_name',

            'execution_group_number',

            'report_sequence_definition_id',
            'report_sequence_definition',
            'report_sequence_definition_name'
        ]