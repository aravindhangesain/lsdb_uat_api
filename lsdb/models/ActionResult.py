from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from lsdb.models import ActionDefinition
from lsdb.models import ActionCompletionDefinition
from lsdb.models import ActionCompletionResult
from lsdb.models import AzureFile
from lsdb.models import Disposition
from lsdb.models import Group
# from models.MeasurementResult import MeasurementResult
# from models.Unit import Unit

# This is ProcedureResult
class ActionResult(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    action_definition = models.ForeignKey('ActionDefinition', on_delete=models.CASCADE,blank=False, null=False)
    completion_criteria = models.ManyToManyField('ActionCompletionDefinition', through='ActionCompletionResult', blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    execution_group = models.FloatField(blank=False, null=False)
    done_datetime = models.DateTimeField(blank=True, null=True)
    start_datetime = models.DateTimeField(blank=True, null=True)
    promise_datetime = models.DateTimeField(blank=True, null=True)
    eta_datetime = models.DateTimeField(blank=True, null=True)
    groups = models.ManyToManyField('Group', blank=True)
    attachments = models.ManyToManyField('AzureFile', blank=True)

    # This may be really necessary, and best done early
    recognized_revenue = models.FloatField(blank=True, null=True)
    # Only way to let mark_complete work without all completion criteria:
    override_description = models.CharField(max_length=128, blank=True, null=True)
    override_user = models.ForeignKey('auth.User', related_name='action_override_user', on_delete=models.CASCADE, blank=True, null=True)
    override_date = models.DateTimeField(blank=True, null=True)

    # This is to try to preempt the multi-inheretance later.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ['name',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
