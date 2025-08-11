from rest_framework import serializers
from lsdb.models import *

class ReportApproverAgendaSerializer(serializers.HyperlinkedModelSerializer):
    report_type = serializers.ReadOnlyField(source='report_result.report_type_definition.name')
    project_number = serializers.ReadOnlyField(source='report_result.work_order.project.number')
    customer_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.customer.name')
    bom = serializers.ReadOnlyField(source='report_result.work_order.name')
    project_manager_name = serializers.ReadOnlyField(source = 'report_result.work_order.project.project_manager.username')
    ntp_date = serializers.ReadOnlyField(source='report_result.work_order.start_datetime')
    author_name = serializers.SerializerMethodField()
    report_version_number = serializers.SerializerMethodField()
    approver_name = serializers.SerializerMethodField()
    approver_id = serializers.SerializerMethodField()
    author_id = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='user.username')
    contractually_obligated_date = serializers.SerializerMethodField()


    def get_contractually_obligated_date(self, obj):
        try:
            report_result_id = obj.report_result
            report_writer_agenda = ReportWriterAgenda.objects.get(report_result=report_result_id)
            return report_writer_agenda.contractually_obligated_date
        except ReportWriterAgenda.DoesNotExist:
            return None
        
    def get_author_name(self,obj):
        try:
            report_type_id =  obj.report_result.report_type_definition
            report_type = ReportTeam.objects.get(report_type = report_type_id)
            return report_type.writer.username
        except ReportTeam.DoesNotExist:
            return None
        
    def get_author_id(self,obj):
        try:
            report_type_id = obj.report_result.report_type_definition
            report_type = ReportTeam.objects.filter(report_type = report_type_id).values_list('writer_id',flat=True).first()
            return report_type
        except ReportTeam.DoesNotExist:
            return None

    def get_approver_id(self,obj):
        try:
            report_type_id = obj.report_result.report_type_definition
            report_type = ReportTeam.objects.get(report_type = report_type_id)
            if report_type.is_projmanager is True:
                return obj.report_result.work_order.project.project_manager.id
            else:
                return report_type.approver.id
        except ReportTeam.DoesNotExist:
            return None
        
    def get_approver_name(self,obj):
        try:            
            report_type_id = obj.report_result.report_type_definition
            report_type = ReportTeam.objects.get(report_type = report_type_id)
            if report_type.is_projmanager is True:
                return obj.report_result.work_order.project.project_manager.username
            else:
                return report_type.approver.username
        except ReportTeam.DoesNotExist:
            return None

    def get_report_version_number(self,obj):
        try:
            report_id = obj.report_result.id
            report_file = ReportFileTemplate.objects.filter(report=report_id).last()
            return report_file.version
        except:
            return "Version not found"
        

    class Meta:
        model = ReportApproverAgenda
        fields  = [
            'id',
            'approver_id',
            'approver_name',
            'report_type',
            'project_number',
            'project_manager_name',
            'customer_name',    
            'ntp_date',
            'bom',
            'report_result',
            'report_result_id',
            'pichina',
            'author_id',
            'author_name',
            'status_pan',
            'contractually_obligated_date',
            'user',
            'username',
            'date_verified',
            'date_approved',
            'date_delivered',
            'date_entered',
            'report_version_number',
            'flag',
            'comments',
            'comment_flag'
        ]