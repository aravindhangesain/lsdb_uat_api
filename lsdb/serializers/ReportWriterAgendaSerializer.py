from rest_framework import serializers
from lsdb.models import *

class ReportWriterAgendaSerializer(serializers.ModelSerializer):
    report_type = serializers.ReadOnlyField(source='report_result.report_type_definition.name')
    project_number = serializers.ReadOnlyField(source='report_result.work_order.project.number')
    customer_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.customer.name')
    bom = serializers.ReadOnlyField(source='report_result.work_order.name')
    project_manager_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.project_manager.username')
    ntp_date = serializers.ReadOnlyField(source='report_result.work_order.start_datetime')
    tech_writer_startdate = serializers.SerializerMethodField()

    def get_tech_writer_startdate(self,obj):
        report_file= ReportFileTemplate.objects.get(report = obj.report_result)
        if report_file:
            return report_file.datetime

    class Meta:
        model = ReportWriterAgenda
        fields  = [
            'id',
            'project_type',
            'report_type',
            'project_number',
            'project_manager_name',
            'customer_name',
            'ntp_date',
            'bom',
            'report_result',
            'pichina',
            'priority',
            'contractually_obligated_date',
            'pqp_version',
            'writer_id',
            'reviewer_id',
            'tech_writer_startdate'
        ]