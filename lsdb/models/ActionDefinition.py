from datetime import datetime
from django.db import models

from lsdb.models import ActionCompletionDefinition
from lsdb.models import Disposition
from lsdb.models import Group

# Tis is a ProcedureDefinition
class ActionDefinition(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    completion_criteria = models.ManyToManyField('ActionCompletionDefinition', blank=True)
    groups = models.ManyToManyField('Group', blank=True)

    class Meta:
        ordering = ('name',)
        unique_together = ['name',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
