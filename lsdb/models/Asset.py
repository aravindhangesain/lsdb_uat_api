from django.db import models
from datetime import datetime
from lsdb.models import AssetType
from lsdb.models import Location
from lsdb.models import Disposition
from lsdb.models import Note
# from models.MeasurementResult import MeasurementResult
# from models.Unit import Unit

class Asset(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=False, null=False)
    last_action_datetime = models.DateTimeField(auto_now_add=True)
    # asset_type = models.ForeignKey('AssetType', related_name='obsolete_asset_type', on_delete=models.CASCADE, blank=False, null=False)
    asset_types = models.ManyToManyField('AssetType', blank=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    notes = models.ManyToManyField('Note', blank=True)

    class Meta:
        ordering = ('name',)
        unique_together = ['name','location']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
'''
asset nesting -- parent asset / apparatus

New columns:
serial number
mfr
model
PO number
Acquisition cost
purchase dates
received date
service date (date put into service)
retirement date (removed from service date)
permanently retired?
useful life (months)
maintenance schedule (days)
depreciation schedule (months)
leased vs owned
Assigned Team -- business unit
Responsible User
primary facility


Asset Groups (?)
- laptops 120 month depreciation
-

Maintenance Records:
planned
unplanned
analytics...

Service records
'''
