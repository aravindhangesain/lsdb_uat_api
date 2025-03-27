from rest_framework import serializers
from lsdb.models import ReportResult,Disposition,UnitReportResult,ProcedureResult,ModuleIntakeDetails,WorkOrder,Project
from django.contrib.auth import get_user_model

class ReportResultSerilaizer(serializers.HyperlinkedModelSerializer):
    
    execution_group_name=serializers.ReadOnlyField(source='report_execution_order.execution_group_name')
    work_order_name=serializers.ReadOnlyField(source='work_order.name')
    report_sequence_definition_name=serializers.ReadOnlyField(source='report_sequence_definition.name')
    product_type_definition_name=serializers.ReadOnlyField(source='product_type_definition.name')
    report_type_definition_name=serializers.ReadOnlyField(source='report_type_definition.name')
    status_disposition_name=serializers.ReadOnlyField(source='status_disposition.name')
    status_disposition = serializers.PrimaryKeyRelatedField(queryset=Disposition.objects.filter(name__in=["Yet To Start", "Completed","In Progress","Issued"]),required=True)
    report_writer_name=serializers.ReadOnlyField(source='report_writer.username')
    report_approver_name=serializers.ReadOnlyField(source='report_approver.username')
    username=serializers.ReadOnlyField(source='user.username')
    hex_color=serializers.SerializerMethodField()
    project_number=serializers.SerializerMethodField()
    azurefile_download=serializers.SerializerMethodField()

    User = get_user_model()
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', required=True)
    
    def get_project_number(self, obj):
        work_order_id=obj.work_order_id
        project_id=WorkOrder.objects.filter(id=work_order_id).values_list('project_id',flat=True).first()

        project_number=Project.objects.filter(id=project_id).values_list('number',flat=True).first()
        return project_number
     
    def get_hex_color(self, obj):
        
        report=ReportResult.objects.filter(id=obj.id).first()

        if report.data_ready_status in ['Module Intake']:
            work_order_id=report.work_order_id

            project_id=WorkOrder.objects.filter(id=work_order_id).values_list('project_id',flat=True).first()
            
            module_intakes=ModuleIntakeDetails.objects.filter(projects_id=project_id)
            if all(intake.steps in ['step 3'] for intake in module_intakes):
                return '#4ef542'
            else:
                return '#f51111'
            
        elif UnitReportResult.objects.filter(report_result_id=obj.id).exists():
            report_result=UnitReportResult.objects.filter(report_result_id=obj.id).first()
            if report_result:
                unit_id=report_result.unit_id
                execution_order=report_result.execution_group_number

                selected_procedures=ProcedureResult.objects.filter(unit_id=unit_id,linear_execution_group=execution_order)
                if all(procedure.disposition_id in [2,10,20] for procedure in selected_procedures):
                    return '#4ef542'
                else:
                    return '#f51111'
            else:
                return '#f5970a'
        elif report.data_ready_status in ['Factory Witness']:
            return '#4ef542'
        
        return '#ff9704'
    
    def get_azurefile_download(self, obj):
        azurefile_id=obj.azurefile_id
        if azurefile_id==None:
            return None
        azurefile_download="https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/"+str(azurefile_id)+"/download"
        return azurefile_download
    
    



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
            'report_approver',
            'report_approver_name',
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
            'azurefile',
            'azurefile_download',
            'hex_color'
        ]
