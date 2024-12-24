from django.db import models

from lsdb.models import Limit
from lsdb.models import StepDefinition
from lsdb.models import ConditionDefinition
from lsdb.models import MeasurementType
from lsdb.models import MeasurementResultType

class MeasurementDefinition(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    limit = models.ForeignKey('Limit', on_delete=models.CASCADE, blank=False, null=False)
    record_only = models.BooleanField(blank=True, null=True)
    allow_skip = models.BooleanField(blank=True, null=True)
    requires_review = models.BooleanField(blank=True, null=True)
    step_definition = models.ForeignKey('StepDefinition', on_delete=models.CASCADE, blank=False, null=False)
    condition_definition = models.ForeignKey('ConditionDefinition', on_delete=models.CASCADE, blank=True, null=True)
    measurement_type = models.ForeignKey('MeasurementType', on_delete=models.CASCADE, blank=False, null=False)
    # measurement_definition = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True) # MeasurementDefinitionGuid?
    # apply_out_of_family_limit = models.BooleanField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    report_order = models.IntegerField(blank=True, null=True)
    measurement_result_type = models.ForeignKey('MeasurementResultType', on_delete=models.CASCADE, blank=False, null=False)


    class Meta:
        ordering = ('name',)
        unique_together =['name','step_definition',
            # 'MeasurementDefinitionGuid',
        ]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
