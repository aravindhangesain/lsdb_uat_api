from django.db import models
from datetime import datetime

from lsdb.models import StepDefinition

class ConditionDefinition(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    # GUIDs were established for these outside of the ID by viewpoint.
    # condition_guid = models.CharField(max_length=32, blank=False, null=False)
    step_definition = models.ForeignKey('StepDefinition', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        ordering = ('name',)
        unique_together = [
            'name',
            # 'condition_guid',
            'step_definition'
        ]
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.name)
