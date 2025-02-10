from django.db import models


class TemplateMaster(models.Model):
    name=models.CharField(max_length=256, blank=True, null=True, unique=True)
    description=models.CharField(max_length=256, blank=True, null=True)
    mapping_type=models.CharField(max_length=256, blank=True, null=True)
    column1=models.CharField(max_length=256, blank=True, null=True)
    column2=models.CharField(max_length=256, blank=True, null=True)
    column3=models.CharField(max_length=256, blank=True, null=True)