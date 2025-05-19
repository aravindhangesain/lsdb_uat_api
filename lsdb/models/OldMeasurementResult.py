from django.db import models


class OldMeasurementResult(models.Model):
    procedure_result = models.ForeignKey('ProcedureResult', on_delete=models.CASCADE)
    imp=models.FloatField(null=True, blank=True)
    pmp=models.FloatField(null=True, blank=True)
    isc=models.FloatField(null=True, blank=True)
    voc=models.FloatField(null=True, blank=True)
    vmp=models.FloatField(null=True, blank=True) 
