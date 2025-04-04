from django.db import models
from django.contrib.auth.models import User



class ProcedureResult_pichina(models.Model):
    unit = models.ForeignKey('Unit_pichina', on_delete=models.CASCADE, blank=True, null=True)
    procedure_definition = models.ForeignKey('ProcedureDefinition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=True, null=True)
    # disposition_codes = models.ManyToManyField('DispositionCode')
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True) # TODO: This might be required
    work_order = models.ForeignKey('Workorder_pichina', on_delete=models.CASCADE, blank=False, null=False)
    linear_execution_group = models.FloatField(blank=False, null=False)
    name = models.CharField(max_length=128, blank=True, null=True)
    work_in_progress_must_comply = models.BooleanField(default=False) # If true must comply, false use to completion
    # group = models.ForeignKey('Group_pichina', on_delete=models.CASCADE, blank=False, null=False)
    supersede = models.BooleanField(blank=True, null=True)
    version = models.CharField(max_length=64, blank=False, null=False)
    test_sequence_definition = models.ForeignKey('TestSequenceDefinition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    allow_skip = models.BooleanField(default=False)
    # notes = models.ManyToManyField('Note', blank=True)

    class Meta:
        ordering = ('linear_execution_group',)
        unique_together =['unit','procedure_definition', 'work_order', 'linear_execution_group', 'start_datetime']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
    # These may need to be in the model or in the serilaizer, but New results can continue an old reult
    # TODO: FillInProcedureResult(old result, new result)
