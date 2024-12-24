from django.db import models

from datetime import datetime

class PermittedView(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False, db_index=True, unique=True)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "{}".format(self.name)
