from django.db import models

class ExpectedUnitType_pichina(models.Model):
    expected_count = models.IntegerField(blank=False, null=False)
    received_count = models.IntegerField(blank=False, null=False)
    project = models.ForeignKey('Project_pichina', on_delete=models.CASCADE, blank=False, null=False)
    unit_type = models.ForeignKey('UnitType_pichina', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        ordering = ('project',)
        unique_together = ['project','unit_type']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{} {}".format(self.project, self.unit_type)
