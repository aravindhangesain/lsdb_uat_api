from django.db import models


class ReportTypeDefinition(models.Model):
    name=models.CharField(max_length=256, blank=True, null=True)
    disposition=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    group=models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)
    version=models.CharField(max_length=256, blank=True, null=True)
    linear_execution_order=models.IntegerField(blank=False, null=False)
    duration=models.IntegerField(blank=True, null=True)