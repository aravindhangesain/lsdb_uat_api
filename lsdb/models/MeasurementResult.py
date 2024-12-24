from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
from lsdb.models import Asset
from lsdb.models import AvailableDefect
from lsdb.models import Disposition
# from lsdb.models import DispositionCode
from lsdb.models import Limit
from lsdb.models import Location
from lsdb.models import MeasurementDefinition
from lsdb.models import MeasurementResultType
from lsdb.models import MeasurementType
# from lsdb.models import OutOfFamilyLimit
from lsdb.models import StepResult

class MeasurementResult(models.Model):
    date_time = models.DateTimeField(blank=True, null=True)
    step_result = models.ForeignKey('StepResult', on_delete=models.CASCADE, blank=False, null=False)
    measurement_definition = models.ForeignKey('MeasurementDefinition', on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=True, null=True)
    # This is a string until I find better info
    software_revision = models.CharField(max_length=32, blank=False, null=False)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=True, null=True)
    # disposition_codes = models.ManyToManyField('DispositionCode')
    result_defect = models.ForeignKey('AvailableDefect', on_delete=models.CASCADE, blank=True, null=True)
    result_double = models.FloatField(blank=True, null=True)
    result_datetime = models.DateTimeField(blank=True, null=True)
    result_string = models.TextField(blank=True, null=True)
    result_boolean = models.BooleanField(blank=True, null=True)
    # TODO: ResultGuid -- Link to another table, table defined in measurement result type
    limit = models.ForeignKey('Limit', on_delete=models.CASCADE, blank=False, null=False)
    # out_of_family_limit= models.ForeignKey('OutOfFamilyLimit', on_delete=models.CASCADE, blank=True, null=True)
    # check reviewed_by_user for duplication (lsdb has 2 for no good reason)
    reviewed_by_user = models.ForeignKey('auth.User', related_name='reviewed_by_user', on_delete=models.CASCADE, blank=True, null=True)
    review_datetime = models.DateTimeField(blank=True, null=True)
    # should deprecate and use notes model
    notes = models.CharField(max_length=128, blank=True, null=True)
    # Do we want actual tags?
    tag = models.CharField(max_length=32, blank=True, null=True)
    station = models.IntegerField(blank=False, null=False)
    start_datetime = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, blank=True, null=True)
    do_not_include = models.BooleanField(default=False)
    name = models.CharField(max_length=32, blank=True, null=True)
    record_only = models.BooleanField(default=False)
    allow_skip = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    measurement_type= models.ForeignKey('MeasurementType', on_delete=models.CASCADE, blank=False, null=False)
    # apply_out_of_family_limit = models.BooleanField(default=False)
    order = models.IntegerField(blank=False, null=False)
    report_order = models.IntegerField(blank=False, null=False)
    measurement_result_type = models.ForeignKey('MeasurementResultType', on_delete=models.CASCADE, blank=False, null=False)
    result_files = models.ManyToManyField('AzureFile', blank=True) # TODO: This may need some voodoo to get right

    class Meta:
        ordering = ('report_order',)
        unique_together =['step_result','measurement_definition', 'date_time']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)

    # These may need to be in the model or in the serilaizer, but New results can continue an old reult
    # TODO: FillInMeasurementResultAndTakeCreditForOldData(old result, new result)
    # TODO: FillInMeasurementResult(old result, new result)
