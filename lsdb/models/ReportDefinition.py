from django.db import models


class ReportDefinition(models.Model):
    report_title=models.CharField(max_length=256, blank=True, null=True)
    report_order_number=models.CharField(max_length=256, blank=True, null=True)
    report_type=models.ForeignKey('ReportType', on_delete=models.CASCADE, blank=False, null=False)
    report_product_type=models.ForeignKey('ReportProductType', on_delete=models.CASCADE, blank=False, null=False)
    column1=models.CharField(max_length=256, blank=True, null=True)
    column2=models.CharField(max_length=256, blank=True, null=True)
    column3=models.CharField(max_length=256, blank=True, null=True)
