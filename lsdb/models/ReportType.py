from django.db import models


class ReportType(models.Model):
    report_name=models.CharField(max_length=256, blank=True, null=True)
    report_shortname=models.CharField(max_length=256, blank=True, null=True)
    column1=models.CharField(max_length=256, blank=True, null=True)
    column2=models.CharField(max_length=256, blank=True, null=True)
    column3=models.CharField(max_length=256, blank=True, null=True)