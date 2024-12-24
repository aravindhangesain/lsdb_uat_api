from django.db import models
from datetime import datetime


class ModuleIntakeImages_pichina(models.Model):
    moduleintake = models.ForeignKey('ModuleIntakeDetails_pichina', on_delete=models.CASCADE, blank=True, null=False)
    label_name = models.CharField(max_length=255, null=False)
    image_path = models.ImageField()
    status = models.CharField(max_length=255, null=True)
    notes = models.CharField(max_length=255, null=True)

