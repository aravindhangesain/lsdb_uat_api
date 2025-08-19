from rest_framework import serializers
from lsdb.models import *


class AssetHistorySerializer(serializers.HyperlinkedModelSerializer):
    serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    asset_name = serializers.ReadOnlyField(source='stepresult.measurementresult.asset.name')
    asset_id = serializers.ReadOnlyField(source='stepresult.measurementresult.asset.id')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    bom = serializers.ReadOnlyField(source='work_order.name')

    class Meta:
        model = ProcedureResult
        fields = [
            'serial_number',
            'asset_name',
            'asset_id',
            'linear_execution_group',
            'name',
            'procedure_definition_name',
            'start_datetime',
            'end_datetime',
            'project_number',
            'customer_name',
            'bom'
        ]