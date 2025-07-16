from django.db import models


class ReportResult(models.Model):
    issue_date=models.DateTimeField(blank=True, null=True)
    due_date=models.DateTimeField(blank=True, null=True)
    report_writer=models.ForeignKey('ReportWriter',blank=True, null=True, on_delete=models.CASCADE)
    report_reviewer=models.ForeignKey('ReportReviewer', blank=True, null=True, on_delete=models.CASCADE)
    data_ready_status=models.CharField(max_length=256, blank=True, null=True)
    user=models.ForeignKey('auth.User', blank=False, null=False, on_delete=models.CASCADE)
    work_order=models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=False, null=False)
    report_sequence_definition=models.ForeignKey('ReportSequenceDefinition', on_delete=models.CASCADE, blank=False, null=False)
    product_type_definition=models.ForeignKey('ProductTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    report_type_definition=models.ForeignKey('ReportTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    status_disposition=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    report_execution_order_number=models.FloatField()
    azurefile=models.ForeignKey('AzureFile', on_delete=models.CASCADE, blank=False, null=False)
    document_title=models.CharField(max_length=256, blank=True, null=True)
    reportexecution_azurefile=models.ForeignKey('AzureFile',null=True,blank=True,on_delete=models.CASCADE,related_name='reportexecution_azurefile')
    ready_datetime = models.DateTimeField(null=True,blank=True)
    hex_color = models.CharField(max_length=120,null=True,blank=True)
    test_sequence_definition=models.ForeignKey('TestSequenceDefinition', on_delete=models.CASCADE, blank=False, null=False)