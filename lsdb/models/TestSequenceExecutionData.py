from django.db import models

from lsdb.models import TestSequenceDefinition
from lsdb.models import WorkOrder


class TestSequenceExecutionData(models.Model):
    test_sequence = models.ForeignKey('TestSequenceDefinition', on_delete=models.CASCADE)
    work_order = models.ForeignKey('WorkOrder', on_delete=models.CASCADE)
    units_required = models.IntegerField(default=0)

    class Meta:
        # ordering = ('execution_group_number',)
        unique_together =['work_order','test_sequence',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{} : {} Units".format(self.test_sequence.name,self.units_required)
