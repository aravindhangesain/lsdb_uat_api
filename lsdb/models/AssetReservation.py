from django.db import models
from datetime import datetime

from lsdb.models import Asset
from lsdb.models import AssetType
from lsdb.models import Location
from lsdb.models import Disposition
from lsdb.models import Note
# from models.MeasurementResult import MeasurementResult
# from models.Unit import Unit

'''
How will this work?
a reservation is created by the user by selecting an asset and a procedure_definition
the start time will be bound by any previous reservations to be start of the next day?

Reservations will be viewed in a gantt form, with the bars representing reservations and
assets are the rows.

unit_reservations represents a list of units that have tickets to ride this reservation.
some other fifo/best match algorithm will assign units from the stress backlog.

'''

class AssetReservation(models.Model):
    asset = models.ManyToManyField('Asset', blank=False)
    procedure_definition = models.ForeignKey('ProcedureDefinition', on_delete=models.CASCADE, blank=False, null=False)
    reservation_capacity = models.IntegerField() # This is probably copied from a capacity elsewhere
    unit_reservations = models.ManyToManyField('Unit', blank=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    start_datetime = models.DateTimeField(auto_now_add=True)
    
    description = models.CharField(max_length=128, blank=True, null=True)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=False, null=False)
    asset_types = models.ManyToManyField('AssetType', blank=True)
    notes = models.ManyToManyField('Note', blank=False)

    class Meta:
        ordering = ('name',)
        unique_together = ['name','location']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
