from django.db import models


class ReportResult(models.Model):
    issue_date=models.DateTimeField(blank=True, null=True)
    due_date=models.DateTimeField(blank=True, null=True)
    report_writer_name=models.CharField(max_length=256, blank=True, null=True)
    report_approver_name=models.CharField(max_length=256, blank=True, null=True)
    data_ready_status=models.CharField(max_length=256, blank=True, null=True)
    # status=models.BooleanField()
    username=models.CharField(max_length=256, blank=True, null=True)
    work_order=models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=False, null=False)
    report_sequence_definition=models.ForeignKey('ReportSequenceDefinition', on_delete=models.CASCADE, blank=False, null=False)
    product_type_definition=models.ForeignKey('ProductTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    report_type_definition=models.ForeignKey('ReportTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    status_disposition=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    report_execution_order_number=models.FloatField()


