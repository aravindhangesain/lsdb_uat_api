from django.db import models

class ProjectTypeDetails(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)