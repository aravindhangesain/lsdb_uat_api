from django.db import models


class ReportProductType(models.Model):
    product_type_name=models.CharField(max_length=256, blank=True, null=True)
    column1=models.CharField(max_length=256, blank=True, null=True)
    column2=models.CharField(max_length=256, blank=True, null=True)