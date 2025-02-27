from django.db import models


class StepResult_pichina(models.Model):
    notes = models.CharField(max_length=128, blank=True, null=True)
    procedure_result = models.ForeignKey('ProcedureResult_pichina', on_delete=models.CASCADE, blank=False, null=False)
    step_definition = models.ForeignKey('StepDefinition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    execution_number = models.IntegerField(blank=False, null=False)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=True, null=True)
    # disposition_codes = models.ManyToManyField('DispositionCode')
    start_datetime = models.DateTimeField(blank=True, null=True)
    duration = models.FloatField( blank=True, null=True)
    # TestStepResultId Guid? (this is for superceding replacment of results)
    # test_step_result = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    archived = models.BooleanField(default=False)
    name = models.CharField(db_index=True, max_length=128, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    step_number = models.CharField(max_length=32, blank=True, null=True)
    step_type = models.ForeignKey('StepType_pichina', on_delete=models.CASCADE, blank=False, null=False)
    linear_execution_group = models.FloatField(blank=False, null=False)
    allow_skip = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)
        unique_together =['name','procedure_result', 'execution_number',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
