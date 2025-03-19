from django.db import models

class UnitReportResult(models.Model):
    procedureresult_name=models.CharField(max_length=120,null=True,blank=True)
    unit=models.ForeignKey('Unit', on_delete=models.CASCADE, blank=True, null=True)
    report_result=models.ForeignKey('ReportResult', on_delete=models.CASCADE, blank=True, null=True)
    execution_group_number=models.FloatField(blank=False, null=False)