from rest_framework import serializers
from lsdb.models import *

class ReportApproverAgendaSerializer(serializers.ModelSerializer):
    report_type = serializers.ReadOnlyField(source='report_result.report_type_definition.name')
    approver_name = serializers.ReadOnlyField(source='approver.name')
    project_number = serializers.ReadOnlyField(source='report_result.work_order.project.number')
    customer_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.customer.name')
    bom = serializers.ReadOnlyField(source='report_result.work_order.name')
    project_manager_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.project_manager.username')
    ntp_date = serializers.ReadOnlyField(source='report_result.work_order.start_datetime')
    author_name = serializers.ReadOnlyField(source = 'author.username')

    class Meta:
        model = ReportApproverAgenda
        fields  = [
            'id',
            'approver',
            'approver_name',
            'report_type',
            'project_number',
            'project_manager_name',
            'customer_name',    
            'ntp_date',
            'bom',
            'report_result',
            'pichina',
            'author',
            'author_name',
            'status_pan',
            'contractually_obligated_date',
            'date_verified',
            'date_approved',
            'date_delivered'
        ]