from rest_framework import serializers
from lsdb.models import *

class ReportWriterAgendaSerializer(serializers.HyperlinkedModelSerializer):
    report_type = serializers.ReadOnlyField(source='report_result.report_type_definition.name')
    project_number = serializers.ReadOnlyField(source='report_result.work_order.project.number')
    customer_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.customer.name')
    bom = serializers.ReadOnlyField(source='report_result.work_order.name')
    project_manager_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.project_manager.username')
    ntp_date = serializers.ReadOnlyField(source='report_result.work_order.start_datetime')
    writer_name = serializers.ReadOnlyField(source='writer.writer_name')
    reviewer_name =serializers.ReadOnlyField(source='reviewer.reviewer_name')
    data_ready_date = serializers.SerializerMethodField()
    data_verification_date = serializers.SerializerMethodField()
    tech_writer_startdate = serializers.SerializerMethodField()

    def get_data_ready_date(self,obj):
        report_result_id = obj.report_result.id
        report_result = ReportResult.objects.get(id = report_result_id)
        if report_result:
            return report_result.ready_datetime
        
    def get_data_verification_date(self,obj):
        report_result_id = obj.report_result.id
        report_result = ReportResult.objects.get(id = report_result_id)
        if report_result:
            return report_result.ready_datetime


    def get_tech_writer_startdate(self,obj):
        report_file= ReportFileTemplate.objects.get(report = obj.report_result)
        if report_file:
            return report_file.datetime

    class Meta:
        model = ReportWriterAgenda
        fields  = [
            'id',
            'url',
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
            'writer',
            'writer_name',
            'reviewer',
            'reviewer_name',
            'tech_writer_startdate',
            'data_ready_date',
            'data_verification_date'
        ]