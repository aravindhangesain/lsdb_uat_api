from django.db import models
from datetime import datetime
from lsdb.models import Customer
from lsdb.models import MeasurementType
from lsdb.models import ModuleProperty
from lsdb.models import AzureFile


class UnitType(models.Model):
    model = models.CharField(max_length=128, blank=False, null=False)
    bom = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    notes = models.CharField(max_length=128, blank=True, null=True)
    manufacturer = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=False, null=False)
    datasheets = models.ManyToManyField('AzureFile', blank=True)
    unit_type_family = models.ForeignKey('UnitTypeFamily', on_delete=models.CASCADE, blank=False, null=False)
    module_property = models.ForeignKey('ModuleProperty', on_delete=models.CASCADE, blank=True, null=True) # TODO: This is invalid for inverters

    class Meta:
        ordering = ('model',)
        unique_together = ['manufacturer','model'] # This solves the serial number collision issue
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "({}) {}".format(
            self.manufacturer.short_name,
            self.model,
            )
