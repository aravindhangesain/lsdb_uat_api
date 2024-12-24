from django.db import models

from lsdb.models import ProcedureDefinition
from lsdb.models import StepDefinition


class StepExecutionOrder(models.Model):
    execution_group_name = models.CharField(max_length=128, blank=False, null=False)
    procedure_definition = models.ForeignKey('ProcedureDefinition', on_delete=models.CASCADE)
    step_definition = models.ForeignKey('StepDefinition', on_delete=models.CASCADE)
    execution_group_number = models.IntegerField()
    allow_skip = models.BooleanField(default=False)

    class Meta:
        ordering = ('execution_group_number',)
        unique_together =['execution_group_name','execution_group_number','procedure_definition', 'step_definition',]
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.execution_group_number)
