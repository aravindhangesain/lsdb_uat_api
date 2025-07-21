from rest_framework import serializers
from lsdb.models import *

class ReportWriterAgendaSerializer(serializers.HyperlinkedModelSerializer):
    report_type_definition_name=serializers.ReadOnlyField(source='report_type_definition.name')
    project_number=serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source = 'work_order.project.customer.name')
    bom = serializers.ReadOnlyField(source='work_order.name')
    project_manager_name = serializers.ReadOnlyField(source = 'work_order.project.project_manager.username')
    ntp_date = serializers.ReadOnlyField(source='work_order.start_datetime')
    data_verification_date = serializers.SerializerMethodField()
    tech_writer_startdate = serializers.SerializerMethodField()
    report_writer_name = serializers.ReadOnlyField(source='report_writer.writer_name')
    report_reviewer_name =serializers.ReadOnlyField(source='report_reviewer.reviewer_name')
    project_type = serializers.SerializerMethodField()
    pichina = serializers.SerializerMethodField()
    priority = serializers.SerializerMethodField()
    contractually_obligated_date = serializers.SerializerMethodField()
    pqp_version = serializers.SerializerMethodField()

    def get_project_number(self, obj):
        work_order_id=obj.work_order_id
        project_id=WorkOrder.objects.filter(id=work_order_id).values_list('project_id',flat=True).first()
        project_number=Project.objects.filter(id=project_id).values_list('number',flat=True).first()
        return project_number

    def get_data_verification_date(self,obj):
            return obj.ready_datetime

    def get_tech_writer_startdate(self, obj):
        report_file = ReportFileTemplate.objects.filter(report=obj,version="v1").first()
        if report_file:
            return report_file.datetime
        return None
    
    def get_project_type(self, obj):
        try:
            report_writer = ReportWriterAgenda.objects.get(report_result=obj.id)
            return report_writer.project_type
        except ReportWriterAgenda.DoesNotExist:
            return None
    
    def get_pichina(self, obj):
        try:
            work_order = obj.work_order  
            project = work_order.project
            location_log = LocationLog.objects.filter(project=project).first()
            if location_log and location_log.location_id in [6, 7, 8]:
                return "yes"
            else:
                return "no"
        except AttributeError:
            return None

        
    def get_priority(self, obj):
        try:
            report_writer = ReportWriterAgenda.objects.get(report_result=obj.id)
            return report_writer.priority
        except ReportWriterAgenda.DoesNotExist:
            return None

    def get_contractually_obligated_date(self, obj):
        try:
            report_writer = ReportWriterAgenda.objects.get(report_result=obj.id)
            return report_writer.contractually_obligated_date
        except ReportWriterAgenda.DoesNotExist:
            return None

    def get_pqp_version(self, obj):
        try:
            report_writer = ReportWriterAgenda.objects.get(report_result=obj.id)
            return report_writer.pqp_version
        except ReportWriterAgenda.DoesNotExist:
            return None
                               
    class Meta:
        model = ReportResult
        fields  = [
            'id',
            'url',
            'report_type_definition_name',
            'project_number',
            'project_manager_name',
            'customer_name',
            'ntp_date',
            'bom',
            'tech_writer_startdate',
            'ready_datetime',
            'data_verification_date',
            'report_writer',
            'report_writer_name',
            'report_reviewer',
            'report_reviewer_name',
            'project_type',
            'pichina',
            'priority',
            'contractually_obligated_date',
            'pqp_version'
        ]