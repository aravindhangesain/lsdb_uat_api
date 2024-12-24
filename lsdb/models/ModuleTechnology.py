from django.db import models
from datetime import datetime

class ModuleTechnology(models.Model):
    name = models.CharField(unique=True, max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    diode_ideality_factor = models.FloatField(default=0)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "{}".format(self.name)
