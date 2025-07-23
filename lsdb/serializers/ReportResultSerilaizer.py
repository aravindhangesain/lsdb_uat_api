from rest_framework import serializers
from lsdb.models import ReportResult,Disposition,WorkOrder,Project
from django.contrib.auth import get_user_model

class ReportResultSerilaizer(serializers.HyperlinkedModelSerializer):
    execution_group_name=serializers.ReadOnlyField(source='report_execution_order.execution_group_name')
    work_order_name=serializers.ReadOnlyField(source='work_order.name')
    report_sequence_definition_name=serializers.ReadOnlyField(source='report_sequence_definition.name')
    product_type_definition_name=serializers.ReadOnlyField(source='product_type_definition.name')
    report_type_definition_name=serializers.ReadOnlyField(source='report_type_definition.name')
    status_disposition_name=serializers.ReadOnlyField(source='status_disposition.name')
    status_disposition = serializers.PrimaryKeyRelatedField(queryset=Disposition.objects.filter(name__in=["Yet To Start", "Completed","In Progress","Issued"]),required=True)
    report_writer_name=serializers.ReadOnlyField(source='report_writer.writer.username')
    report_reviewer_name=serializers.ReadOnlyField(source='report_reviewer.reviewer.username')
    username=serializers.ReadOnlyField(source='user.username')
    project_number=serializers.SerializerMethodField()
    azurefile_download=serializers.SerializerMethodField()
    reportexecution_azurefile=serializers.SerializerMethodField()

    User = get_user_model()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', required=True)

    def get_project_number(self, obj):
        work_order_id=obj.work_order_id
        project_id=WorkOrder.objects.filter(id=work_order_id).values_list('project_id',flat=True).first()
        project_number=Project.objects.filter(id=project_id).values_list('number',flat=True).first()
        return project_number
    
    def get_azurefile_download(self, obj):
        azurefile_id=obj.azurefile_id
        if azurefile_id==None:
            return None
        azurefile_download="https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/"+str(azurefile_id)+"/download"
        return azurefile_download
    
    def get_reportexecution_azurefile(self, obj):
        int_var = obj.reportexecution_azurefile_id
        if int_var:
            return f"https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/{int_var}/download"
        return None
   
    class Meta:
        model=ReportResult
        fields=[
            'id',
            'url',
            'document_title',
            'issue_date',
            'due_date',
            'report_writer',
            'report_writer_name',
            'report_reviewer',
            'report_reviewer_name',
            'data_ready_status',
            'user',
            'user_id',
            'username',
            'work_order_id',
            'work_order_name',
            'project_number',
            'report_sequence_definition_id',
            'report_sequence_definition_name',
            'product_type_definition_id',
            'product_type_definition_name',
            'report_type_definition_id',
            'report_type_definition_name',
            'status_disposition',
            'status_disposition_name',
            'report_execution_order_number',
            'execution_group_name',
            'hex_color',
            'azurefile',
            'azurefile_download',
            'reportexecution_azurefile'
        ]