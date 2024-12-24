from django.db import models

from datetime import datetime
from lsdb.models import Disposition
from lsdb.models import ProcedureExecutionOrder
from lsdb.models import ProcedureDefinition
from lsdb.models import Group
from lsdb.models import UnitTypeFamily

class TestSequenceDefinition(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    short_name = models.CharField(max_length=16, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    notes = models.CharField(max_length=128, blank=True, null=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    # disposition_codes = models.ManyToManyField('DispositionCode', null=True)
    procedure_definitions = models.ManyToManyField('ProcedureDefinition', through='ProcedureExecutionOrder')
    version = models.CharField(max_length=32, blank=False, null=False)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)
    unit_type_family = models.ForeignKey('UnitTypeFamily', on_delete=models.CASCADE, blank=False, null=False)
    hex_color = models.CharField(max_length=7, blank=False, null=False)

    class Meta:
        ordering = ('name',)
        unique_together =['name','group', 'version', 'unit_type_family']
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.name)
