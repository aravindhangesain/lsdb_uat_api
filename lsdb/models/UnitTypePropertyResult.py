from django.db import models

from datetime import datetime
from lsdb.models import UnitType
from lsdb.models import UnitTypePropertyType

class UnitTypePropertyResult(models.Model):
    unit_type = models.ForeignKey('UnitType', on_delete=models.CASCADE, blank=False, null=False)
    unit_type_property_type = models.ForeignKey('UnitTypePropertyType', on_delete=models.CASCADE, blank=False, null=False)
    value_double = models.FloatField(blank=True, null=True)
    value_datetime = models.DateTimeField(auto_now_add=True)
    value_string = models.CharField(max_length=32, blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)

    class Meta:
        # ordering = ('name',)
        unique_together =['unit_type','unit_type_property_type',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{} {}".format(self.unit_type, self.unit_type_property_type)
