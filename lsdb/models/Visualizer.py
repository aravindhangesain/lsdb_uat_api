from django.db import models
from datetime import datetime

# This code is a stub and probably going away with plugins
class Visualizer(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        ordering = ('name',)
        unique_together = ['name']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
