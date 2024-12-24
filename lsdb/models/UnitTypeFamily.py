from django.db import models
from datetime import datetime
from lsdb.models import MeasurementType


class UnitTypeFamily(models.Model):
    name = models.CharField(db_index=True, unique=True, max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    measurement_types = models.ManyToManyField('MeasurementType')

    class Meta:
        ordering = ('name',)
        # unique_together = ['customer','model','bom'] # This solves the serial number collision issue
        # indexes = [
        #     models.Index(fields=unique_together)
        # ]
    def __str__(self):
        return "{}".format(self.name)
