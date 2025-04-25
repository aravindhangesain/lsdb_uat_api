from rest_framework import serializers
from lsdb.models import ReportExecutionOrder

class ReportExecutionOrderSerializer(serializers.HyperlinkedModelSerializer):
    report_definition_name=serializers.ReadOnlyField(source='report_definition.name')
    product_definition_name=serializers.ReadOnlyField(source='product_definition.name')
    report_sequence_definition_name=serializers.ReadOnlyField(source='report_sequence_definition.name')

    name=serializers.ReadOnlyField(source='report_sequence_definition.name')
    short_name=serializers.ReadOnlyField(source='report_sequence_definition.short_name')
    description=serializers.ReadOnlyField(source='report_sequence_definition.description')
    disposition=serializers.ReadOnlyField(source='report_sequence_definition.disposition.id')
    disposition_name=serializers.ReadOnlyField(source='report_sequence_definition.disposition.name')
    version=serializers.ReadOnlyField(source='report_sequence_definition.version')
    disposition_url=serializers.SerializerMethodField()
    
    azure_file_download_url=serializers.SerializerMethodField()

    def get_disposition_url(self, obj):
        if obj.report_sequence_definition and obj.report_sequence_definition.disposition:
            return f"https://lsdbhaveblueuat.azurewebsites.net/api/1.0/dispositions/{obj.report_sequence_definition.disposition.id}/"
        return None
    
    def get_azure_file_download_url(self, obj):
        azurefile_id=obj.azure_file_id
        if azurefile_id==None:
            return None
        azurefile_download_url="https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/"+str(azurefile_id)+"/download"
        return azurefile_download_url


        




    class Meta:
        model=ReportExecutionOrder
        fields=[
            'id',
            'url',
            'execution_group_name',
            'report_definition_id',
            'report_definition',
            'report_definition_name',

            'product_definition_id',
            'product_definition',
            'product_definition_name',

            'execution_group_number',

            'report_sequence_definition_id',
            'report_sequence_definition',
            'report_sequence_definition_name',

            'name',
            'short_name',
            'description',
            'disposition',
            'disposition_url',
            'disposition_name',
            'version',
            'azure_file',
            'azure_file_download_url',
            'data_ready_status',
        ]