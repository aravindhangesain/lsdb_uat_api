from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation

from datetime import datetime
from lsdb.models import Customer
from lsdb.models import Group
from lsdb.models import Disposition
from lsdb.models import Unit
from lsdb.models import Note
from lsdb.models import ExpectedUnitType

class Project(models.Model):
    notes = models.ManyToManyField('Note', blank=True)
    sri_notes = models.ManyToManyField('Note', related_name='sri_notes', blank=True)
    number = models.CharField(max_length=32, blank=False, null=False)
    sfdc_number = models.CharField(max_length=32, blank=True, null=True)
    project_manager = models.ForeignKey('auth.User', blank=False, null=False, on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', blank=False, null=False, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)
    start_date = models.DateField(blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    units = models.ManyToManyField('Unit', blank=True)
    proposal_price = models.FloatField(blank=True, null=True)
    attachments = models.ManyToManyField('AzureFile', blank=True)
    actions = GenericRelation('ActionResult')
    # is_pvel = models.BooleanField(default=False, null=False, blank=False)
    # location = models.ForeignKey('Location', blank=False, null=True, on_delete=models.CASCADE)
    # unit_disposition = (return/destroy)
    # expected_unit_types = models.ManyToManyField('ExpectedUnitType', blank=True)

    class Meta:
        ordering = ('number',)
        unique_together =['number','group']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.number)
