from django.db import models

from lsdb.models import ActionPlanDefinition
from lsdb.models import ActionDefinition

# This is ProcedureExecutionOrder
class ActionExecutionOrder(models.Model):
    execution_group_number = models.FloatField()
    execution_group_name = models.CharField(max_length=128, blank=True, null=True)
    action_plan = models.ForeignKey('ActionPlanDefinition', on_delete=models.CASCADE)
    action_definition = models.ForeignKey('ActionDefinition', on_delete=models.CASCADE)

    class Meta:
        unique_together =['execution_group_number','action_definition', 'action_plan',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{} : {}".format(self.execution_group_number,self.execution_group_name)
