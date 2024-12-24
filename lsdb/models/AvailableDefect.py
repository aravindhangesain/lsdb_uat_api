from django.db import models
from datetime import datetime

class AvailableDefect(models.Model):
    category = models.CharField(max_length=32, blank=False, null=False)
    short_name = models.CharField(max_length=64, blank=False, null=False)
    description = models.TextField(blank=False, null=False)

    class Meta:
        ordering = ('category',)
        unique_together = ['category','short_name']
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.short_name)
