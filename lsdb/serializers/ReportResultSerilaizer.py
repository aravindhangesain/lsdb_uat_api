from rest_framework import serializers
from lsdb.models import ReportResult


class ReportResultSerilaizer(serializers.ModelSerializer):

    execution_group_name=serializers.ReadOnlyField(source='report_execution_order.execution_group_name')

    class Meta:
        model=ReportResult
        fields=[
            'id',
            'url',
            'issue_date',
            'due_date',
            'report_writer_name',
            'report_approver_name',
            'data_ready_status',
            'status',
            'username',
            'work_order_id',
            'report_sequence_definition_id',
            'product_type_definition_id',
            'report_type_definition_id',
            'disposition_id',
            'report_execution_order_number',
            'execution_group_name'
        ]