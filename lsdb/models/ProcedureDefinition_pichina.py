from django.db import models


class ProcedureDefinition_pichina(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    work_in_progress_must_comply = models.BooleanField(default=False) # If true must comply, false use to completion
    group = models.ForeignKey('Group_pichina', on_delete=models.CASCADE, blank=False, null=False)
    supersede = models.BooleanField(blank=True, null=True)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    version = models.CharField(max_length=32, blank=False, null=False)
    # unit_type_family = models.ForeignKey('UnitTypeFamily', on_delete=models.CASCADE, blank=False, null=False)
    # asset_types = models.ManyToManyField('AssetType')
    # step_definitions = models.ManyToManyField('StepDefinition_pichina', through='StepExecutionOrder')
    linear_execution_group = models.IntegerField(blank=False, null=False)
    visualizer = models.ForeignKey('Visualizer_pichina', on_delete=models.CASCADE, blank=False, null=False)
    project_weight = models.IntegerField(default=1, blank=False, null=False) # to replace measurement math
    aggregate_duration = models.IntegerField(default=1, blank=False, null=False) # in minutes, all steps added together 

    class Meta:
        ordering = ('name',)
        unique_together =['name', 'version',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
