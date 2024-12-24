from django.db import models
from datetime import datetime


class NewCrateIntake(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=True, null=True)
    manufacturer = models.CharField(max_length=128, blank=True, null=True)
    crate_intake_date = models.DateField(blank=True,null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.CharField(max_length=128, blank=True, null=True)
    created_on = models.DateField(blank=True,null=True)
    crate_name = models.CharField(max_length=128, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.created_on:
            self.created_on = datetime.now().strftime('%Y-%m-%d')
        super().save(*args, **kwargs)
    