from django.db import models

class TestSequenceDefinition_pichina(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    short_name = models.CharField(max_length=16, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    notes = models.CharField(max_length=128, blank=True, null=True)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    # disposition_codes = models.ManyToManyField('DispositionCode', null=True)
    procedure_definitions = models.ManyToManyField('ProcedureDefinition_pichina', through='ProcedureExecutionOrder_pichina')
    version = models.CharField(max_length=32, blank=False, null=False)
    group = models.ForeignKey('Group_pichina', on_delete=models.CASCADE, blank=False, null=False)
    # unit_type_family = models.ForeignKey('UnitTypeFamily', on_delete=models.CASCADE, blank=False, null=False)
    hex_color = models.CharField(max_length=7, blank=False, null=False)

    class Meta:
        ordering = ('name',)
        unique_together =['name','group', 'version']
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.name)
