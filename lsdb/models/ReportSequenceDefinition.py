from django.db import models


class ReportSequenceDefinition(models.Model):
    name=models.CharField(max_length=256, blank=True, null=True,unique=True)
    short_name=models.CharField(max_length=256, blank=True, null=True)
    description=models.CharField(max_length=256, blank=True, null=True)
    disposition=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    version=models.CharField(max_length=256,blank=True, null=True)
    created_date=models.DateTimeField(blank=True, null=True)
    hex_color=models.CharField(max_length=7, blank=False, null=False)
  
