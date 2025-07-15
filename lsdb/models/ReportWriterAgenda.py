from django.db import models

class ReportWriterAgenda(models.Model):
    project_type = models.CharField(max_length=32,null=True,blank=True)
    report_result = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    pichina = models.CharField(max_length=32,null=True,blank=True)
    priority = models.CharField(max_length=32,null=True,blank=True)
    contractually_obligated_date = models.DateTimeField(null=True,blank=True)
    pqp_version = models.CharField(max_length=32,null=True,blank=True)
    writer= models.ForeignKey('ReportWriter',on_delete=models.CASCADE,null=True,blank=True)
    reviewer= models.ForeignKey('ReportReviewer',on_delete=models.CASCADE,null=True,blank=True)