from django.db import models

class ReportApproverAgenda(models.Model):
    approver = models.ForeignKey('ReportTeam',on_delete=models.CASCADE,null=True,blank=True)
    report_result = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    pichina = models.CharField(max_length=32,null=True,blank=True)
    author = models.ForeignKey('ReportTeam',related_name = 'author',on_delete=models.CASCADE,null=True,blank=True)
    contractually_obligated_date = models.DateTimeField(null=True,blank=True)
    status_pan = models.CharField(max_length=32,null=True,blank=True)
    date_verified = models.DateTimeField(null=True,blank=True)
    date_approved = models.DateTimeField(null=True,blank=True)
    date_delivered = models.DateTimeField(null=True,blank=True)
    date_entered = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    verified_comment = models.TextField(null=True, blank=True)
    approved_comment = models.TextField(null=True, blank=True)
    delivered_comment = models.TextField(null=True, blank=True)
    flag=models.BooleanField()
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
