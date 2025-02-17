from django.db import models


class ReportResult(models.Model):
    issue_date=models.DateTimeField(blank=True, null=True)
    due_date=models.DateTimeField(blank=True, null=True)
    report_writer_name=models.CharField(max_length=256, blank=True, null=True)
    report_approver_name=models.CharField(max_length=256, blank=True, null=True)
    data_ready_status=models.BooleanField()
    status=models.BooleanField()
    report_type=models.CharField(max_length=256, blank=True, null=True)
    report_sequence=models.CharField(max_length=256, blank=True, null=True)
    