from django.db import models

class MeasurementCorrectionFactor(models.Model):
    new_procedure_result_id=models.IntegerField(blank=True, null=True)
    old_procedure_result_id=models.IntegerField(blank=True, null=True)