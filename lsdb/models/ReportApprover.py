from django.db import models

class ReportApprover(models.Model):
    approver_name = models.CharField(max_length=150,null=True,blank=True)
    report_type = models.ForeignKey('ReportTypeDefinition',on_delete=models.CASCADE,null=True,blank=True)