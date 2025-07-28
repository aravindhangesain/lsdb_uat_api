from django.db import models

class ReportWriterAgenda(models.Model):
    report_result = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    tech_writer_start_date = models.DateTimeField(null=True,blank=True)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    contractually_obligated_date = models.DateTimeField(null=True,blank=True)
