from django.db import models

class ReportApproverNote(models.Model):
    report = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    subject = models.CharField(max_length=256, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    type =  models.ForeignKey('NoteType',on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    approver = models.ForeignKey('ReportApprover',on_delete=models.CASCADE,null=True,blank=True)