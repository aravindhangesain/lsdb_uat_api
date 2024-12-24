from django.db import models

class MeasurementResult_pichina(models.Model):
    date_time = models.DateTimeField(blank=True, null=True)
    step_result = models.ForeignKey('StepResult_pichina', on_delete=models.CASCADE, blank=False, null=False)
    measurement_definition = models.ForeignKey('MeasurementDefinition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey('AuthUser_pichina', on_delete=models.CASCADE, blank=True, null=True)
    location = models.ForeignKey('Location_pichina', on_delete=models.CASCADE, blank=True, null=True)
    software_revision = models.CharField(max_length=32, blank=False, null=False)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=True, null=True)
    disposition_codes = models.ManyToManyField('DispositionCode_pichina')
    result_defect = models.ForeignKey('AvailableDefect_pichina', on_delete=models.CASCADE, blank=True, null=True)
    result_double = models.FloatField(blank=True, null=True)
    result_datetime = models.DateTimeField(blank=True, null=True)
    result_string = models.TextField(blank=True, null=True)
    result_boolean = models.BooleanField(blank=True, null=True)
    # limit = models.ForeignKey('Limit', on_delete=models.CASCADE, blank=False, null=False)
    # out_of_family_limit= models.ForeignKey('OutOfFamilyLimit', on_delete=models.CASCADE, blank=True, null=True)
    reviewed_by_user = models.ForeignKey('AuthUser_pichina', related_name='reviewed_by_user', on_delete=models.CASCADE, blank=True, null=True)
    review_datetime = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=128, blank=True, null=True)
    tag = models.CharField(max_length=32, blank=True, null=True)
    station = models.IntegerField(blank=False, null=False)
    start_datetime = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    asset = models.ForeignKey('Asset_pichina', on_delete=models.CASCADE, blank=True, null=True)
    do_not_include = models.BooleanField(default=False)
    name = models.CharField(max_length=32, blank=True, null=True)
    record_only = models.BooleanField(default=False)
    allow_skip = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    measurement_type= models.ForeignKey('MeasurementType_pichina', on_delete=models.CASCADE, blank=False, null=False)
    # apply_out_of_family_limit = models.BooleanField(default=False)
    order = models.IntegerField(blank=False, null=False)
    report_order = models.IntegerField(blank=False, null=False)
    measurement_result_type = models.ForeignKey('MeasurementResultType_pichina', on_delete=models.CASCADE, blank=False, null=False)
    result_files = models.ManyToManyField('AzureFile_pichina', related_name='measurementresult_result_files_pichina',through='MeasurementResultResultFilesPichina',blank=True)

    class Meta:
        ordering = ('report_order',)
        unique_together =['step_result','date_time']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)

