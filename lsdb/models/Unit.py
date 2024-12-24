from django.db import models
from datetime import datetime
from lsdb.models import Asset
from lsdb.models import AzureFile
from lsdb.models import Crate
from lsdb.models import Disposition
from lsdb.models import Location
from lsdb.models import Note
from lsdb.models import UnitType



class Unit(models.Model):
    unit_type = models.ForeignKey('UnitType', on_delete=models.CASCADE, blank=False, null=False)
    fixture_location = models.ForeignKey('Asset', on_delete=models.CASCADE, blank=True, null=True)
    crate = models.ForeignKey('Crate', on_delete=models.CASCADE, blank=False, null=False)
    serial_number = models.CharField(max_length=128, blank=False, null=False) # TODO: C# depended on this being unique
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    notes = models.ManyToManyField('Note', blank=True)
    old_notes = models.CharField(max_length=128, blank=True, null=True)
    unit_images = models.ManyToManyField('AzureFile', blank=True) # TODO: This may need some voodoo to get right
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False,
        default=16)
    tib = models.BooleanField(blank=True, null=True)
    intake_date = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ('serial_number',)
        unique_together = ['serial_number','unit_type'] # This solves the serial number collision issue
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{} {}".format(
            self.unit_type.model,
            self.serial_number,
            )
