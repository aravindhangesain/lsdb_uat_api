from django.db import models
from datetime import datetime
from lsdb.models import ActionDefinition
from lsdb.models import ActionExecutionOrder
from lsdb.models import Disposition
from lsdb.models import Group
from lsdb.models import UnitTypeFamily

# This is a TSD:
class ActionPlanDefinition(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    action_definitions = models.ManyToManyField('ActionDefinition', through='ActionExecutionOrder')
    groups = models.ManyToManyField('Group', blank=True)
    unit_type_family = models.ForeignKey('UnitTypeFamily', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        ordering = ('name',)
        unique_together = ['name',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
