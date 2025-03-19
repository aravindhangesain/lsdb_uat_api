from django.db import models


class ReportResult(models.Model):
    issue_date=models.DateTimeField(blank=True, null=True)
    due_date=models.DateTimeField(blank=True, null=True)
    report_writer=models.ForeignKey('auth.User', related_name ='writer',blank=False, null=False, on_delete=models.CASCADE)
    report_approver=models.ForeignKey('auth.User', related_name ='approver',blank=False, null=False, on_delete=models.CASCADE)
    data_ready_status=models.CharField(max_length=256, blank=True, null=True)
    # status=models.BooleanField()
    user=models.ForeignKey('auth.User', blank=False, null=False, on_delete=models.CASCADE)
    work_order=models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=False, null=False)
    report_sequence_definition=models.ForeignKey('ReportSequenceDefinition', on_delete=models.CASCADE, blank=False, null=False)
    product_type_definition=models.ForeignKey('ProductTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    report_type_definition=models.ForeignKey('ReportTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    status_disposition=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    report_execution_order_number=models.FloatField()
    azurefile=models.ForeignKey('AzureFile', on_delete=models.CASCADE, blank=False, null=False)


