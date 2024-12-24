from django.db import models
from datetime import datetime

from lsdb.models import StepType

class StepDefinition(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    linear_execution_group = models.IntegerField(blank=False, null=False)
    step_type = models.ForeignKey('StepType', on_delete=models.CASCADE, blank=False, null=False)


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "{}".format(self.name)
