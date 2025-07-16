from django.db import models

class ReportFileTemplate(models.Model):
    report = models.ForeignKey("ReportResult",on_delete=models.CASCADE,blank=False, null=False)
    workorder = models.ForeignKey("WorkOrder",on_delete=models.CASCADE,blank=False, null=False)
    file = models.FileField(blank=False, null=False)
    name=models.CharField(max_length=100,null=True,blank=True)
    user= models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    datetime = models.DateTimeField(null=True,blank=True)
    version = models.CharField(max_length=150, null=True, blank=True)