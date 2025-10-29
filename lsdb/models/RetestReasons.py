from django.db import models

class RetestReasons(models.Model):
    reason = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)