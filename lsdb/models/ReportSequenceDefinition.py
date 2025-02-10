from django.db import models


class ReportSequenceDefinition(models.Model):
    name=models.CharField(max_length=256, blank=True, null=True)
    shortname=models.CharField(max_length=256, blank=True, null=True)
    description=models.CharField(max_length=256, blank=True, null=True)
    disposition_id=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    version=models.FloatField(blank=True, null=True)
    created_date=models.DateTimeField(blank=True, null=True)
    report_definition=models.ForeignKey('ReportDefinition', on_delete=models.CASCADE, blank=False, null=False)
    column1=models.CharField(max_length=256, blank=True, null=True)
    column2=models.CharField(max_length=256, blank=True, null=True)
    column3=models.CharField(max_length=256, blank=True, null=True)