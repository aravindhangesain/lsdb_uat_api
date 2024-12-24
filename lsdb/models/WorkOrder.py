from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from datetime import datetime
from lsdb.models import Project
from lsdb.models import Unit
from lsdb.models import Disposition
# from lsdb.models import DispositionCode
from lsdb.models import TestSequenceDefinition
from lsdb.models import TestSequenceExecutionData

class WorkOrder(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=False, null=False)
    start_datetime = models.DateTimeField(blank=True, null=True) # NTP Date
    units = models.ManyToManyField('Unit', blank=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    # disposition_codes = models.ManyToManyField('DispositionCode', blank=False)
    test_sequence_definitions = models.ManyToManyField('TestSequenceDefinition', blank=True, through='TestSequenceExecutionData')
    tib = models.BooleanField(blank=True, null=True) # "Temporarily Imported under Bond"
    unit_disposition = models.ForeignKey('Disposition', related_name='unitdisposition',
        on_delete=models.CASCADE, blank=False, null=False, default=23) # recycle after 30 days
    actions = GenericRelation('ActionResult')

    class Meta:
        ordering = ('name',)
        unique_together =['name','project',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
