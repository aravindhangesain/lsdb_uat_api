from django.db import models

from lsdb.models import TestSequenceDefinition
from lsdb.models import ProcedureDefinition


class ProcedureExecutionOrder(models.Model):
    execution_group_name = models.CharField(max_length=128, blank=True, null=True)
    test_sequence = models.ForeignKey('TestSequenceDefinition', on_delete=models.CASCADE)
    procedure_definition = models.ForeignKey('ProcedureDefinition', on_delete=models.CASCADE)
    execution_group_number = models.FloatField()
    repetition_group_number = models.IntegerField(blank=True, null=True)
    allow_skip = models.BooleanField()
    # This is dangerous: if the condition here is True, then the procedure is executed.
    execution_condition = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        ordering = ('execution_group_number',)
        unique_together =['execution_group_number','procedure_definition', 'test_sequence',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{} : {}".format(self.execution_group_number,self.execution_group_name)
