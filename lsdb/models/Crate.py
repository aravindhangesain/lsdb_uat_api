from django.db import models

from lsdb.models import AzureFile
from lsdb.models import Customer
from lsdb.models import Disposition
from lsdb.models import Note
from lsdb.models import Project
from lsdb.models import WorkOrder

class Crate(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    shipped_by = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=False, null=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True)
    crate_images = models.ManyToManyField('AzureFile', blank=True)
    received_date = models.DateTimeField(null=False, blank=False)
    notes = models.ManyToManyField('Note', blank=True)
    shipping_agent = models.CharField(max_length=128, blank=True, null=True)
    work_orders = models.ManyToManyField('WorkOrder', blank=True)

    class Meta:
        ordering = ('name',)
        unique_together =['name','shipped_by']
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.name)
