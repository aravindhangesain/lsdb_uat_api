from django.db import models
from datetime import datetime


class CrateIntakeImages(models.Model):
    newcrateintake = models.ForeignKey('NewCrateIntake', on_delete=models.CASCADE, blank=True, null=False)
    label_name = models.CharField(max_length=255, null=False)
    image_path = models.ImageField()
    uploaded_date = models.DateField(blank=True, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=255, null=True)
    notes = models.CharField(max_length=255, null=True)


    def save(self, *args, **kwargs):
        if not self.uploaded_date:
            self.uploaded_date = datetime.now().strftime('%Y-%m-%d')
        super().save(*args, **kwargs)