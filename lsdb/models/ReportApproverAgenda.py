from django.db import models

class ReportApproverAgenda(models.Model):
    approver = models.ForeignKey('ReportApprover',on_delete=models.CASCADE,null=True,blank=True)
    report_result = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    pichina = models.CharField(max_length=32,null=True,blank=True)
    author = models.CharField(max_length=32,null=True,blank=True)
    contractually_obligated_date = models.DateTimeField(null=True,blank=True)
    status_pan = models.CharField(max_length=32,null=True,blank=True)
    date_verified = models.DateTimeField(null=True,blank=True)
    date_approved = models.DateTimeField(null=True,blank=True)
    date_delivered = models.DateTimeField(null=True,blank=True)