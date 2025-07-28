from rest_framework import serializers
from lsdb.models import *
from urllib.parse import quote
from datetime import timedelta
from datetime import date


AZURE_BLOB_BASE_URL = "https://haveblueazdev.blob.core.windows.net/reportmedia/"

class ReportWriterAgendaSerializer(serializers.ModelSerializer):
    report_type_definition_name=serializers.ReadOnlyField(source='report_type_definition.name')
    project_number=serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source = 'work_order.project.customer.name')
    bom = serializers.ReadOnlyField(source='work_order.name')
    project_manager_name = serializers.ReadOnlyField(source = 'work_order.project.project_manager.username')
    ntp_date = serializers.ReadOnlyField(source='work_order.start_datetime')
    data_verification_date = serializers.SerializerMethodField()
    tech_writer_startdate = serializers.SerializerMethodField()
    report_writer_name = serializers.SerializerMethodField()
    report_reviewer_name =serializers.SerializerMethodField()
    project_type = serializers.SerializerMethodField()
    priority = serializers.SerializerMethodField()
    contractually_obligated_date = serializers.SerializerMethodField()
    pqp_version = serializers.SerializerMethodField()
    project_id = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()
    report_writer_id = serializers.SerializerMethodField()
    report_reviewer_id = serializers.SerializerMethodField()
    report_file  = serializers.SerializerMethodField()

    def get_report_file(self, obj):
        report_file = ReportFileTemplate.objects.filter(report=obj.id).order_by('-id').first()
        if report_file and report_file.file:
            filename = report_file.file.name
            if filename.startswith("reportmedia/"):
                filename = filename.replace("reportmedia/", "")
            encoded_filename = quote(filename)
            return AZURE_BLOB_BASE_URL + encoded_filename
        return None
    
    def get_project_number(self, obj):
        work_order_id=obj.work_order_id
        project_id=WorkOrder.objects.filter(id=work_order_id).values_list('project_id',flat=True).first()
        project_number=Project.objects.filter(id=project_id).values_list('number',flat=True).first()
        return project_number
    
    def get_customer_id(self,obj):
        project_id = obj.work_order.project_id
        customer_id = Project.objects.filter(id=project_id).values_list('customer_id', flat=True).first()
        return customer_id
    
    def get_project_id(self, obj):
        work_order_id = obj.work_order_id
        project_id = WorkOrder.objects.filter(id=work_order_id).values_list('project_id', flat=True).first()
        return project_id

    def get_data_verification_date(self,obj):
            return obj.ready_datetime

    def get_tech_writer_startdate(self, obj):
        report_id = ReportWriterAgenda.objects.filter(report_result=obj).first()
        if report_id:
            return report_id.tech_writer_start_date
        return None
    
    def get_project_type(self, obj):
        try:
            project = Project.objects.filter(id=obj.work_order.project_id).first()
            project_type = ProjectType.objects.get(project = project)
            return project_type.project_type
        except ProjectType.DoesNotExist:
            return None

        
    def get_priority(self, obj):
        try:
            report_writer = ReportWriterAgenda.objects.get(report_result=obj.id)
            if report_writer.contractually_obligated_date:
                delta = report_writer.contractually_obligated_date.date() - date.today()
                # priority = delta.days - 11
                return delta.days
            return None
        except ReportWriterAgenda.DoesNotExist:
            return None
        
    def get_contractually_obligated_date(self, obj):
        try:
            report_writer, created = ReportWriterAgenda.objects.get_or_create(report_result=obj)
            if report_writer.contractually_obligated_date:
                return report_writer.contractually_obligated_date
            report_type = obj.report_type_definition
            report_team = ReportTeam.objects.filter(report_type=report_type).first()
            if not report_team or not report_team.obligated_date:
                return None
            try:
                days_to_add = int(report_team.obligated_date)
            except ValueError:
                return None
            work_order = obj.work_order 
            ntp_date = getattr(work_order, "start_datetime", None)
            if not ntp_date:
                return None
            calculated_date = ntp_date + timedelta(days=days_to_add)
            report_writer.contractually_obligated_date = calculated_date
            report_writer.save()
            return calculated_date
        except Exception as e:
            return None


    def get_pqp_version(self, obj):
        try:
            report_sequence_definition = obj.report_sequence_definition
            report = ReportExecutionOrder.objects.filter(
                report_sequence_definition=report_sequence_definition
            ).first()
            if report and report .test_definition:
                return report .test_definition.version
            return None
        except Exception as e:
            return None 
        
    def get_report_writer_name(self,obj):
        try:
            report_type_id = obj.report_type_definition
            report_type = ReportTeam.objects.get(report_type = report_type_id)
            return report_type.writer.username
        except ReportTeam.DoesNotExist:
            return None
    
    def get_report_reviewer_name(self,obj):
        try:
            report_type_id = obj.report_type_definition
            report_type = ReportTeam.objects.get(report_type = report_type_id)
            return report_type.reviewer.username
        except ReportTeam.DoesNotExist:
            return None
        
    def get_report_writer_id(self,obj):
        try:
            report_type_id = obj.report_type_definition
            report_type = ReportTeam.objects.filter(report_type = report_type_id).values_list('writer_id',flat=True).first()
            return report_type
        except ReportTeam.DoesNotExist:
            return None
    
    def get_report_reviewer_id(self,obj):
        try:
            report_type_id = obj.report_type_definition
            report_type = ReportTeam.objects.filter(report_type = report_type_id).values_list('reviewer_id',flat=True).first()
            return report_type
        except ReportTeam.DoesNotExist:
            return None
        
                               
    class Meta:
        model = ReportResult
        fields  = [
            'id',
            'url',
            'report_type_definition_name',
            'project_id',
            'project_number',
            'project_manager_name',
            'customer_id',
            'customer_name',
            'ntp_date',
            'work_order',
            'bom',
            'tech_writer_startdate',
            'ready_datetime',
            'data_verification_date',
            'report_writer_id',
            'report_writer_name',
            'report_reviewer_id',
            'report_reviewer_name',
            'project_type',
            'priority',
            'contractually_obligated_date',
            'pqp_version',
            'report_file'
        ]