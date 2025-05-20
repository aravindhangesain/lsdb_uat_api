from django.db import models

class VisualInspection(models.Model):
    procedure_result = models.ForeignKey('ProcedureResult',on_delete=models.CASCADE,blank=True, null=True)
    procedure_definition = models.ForeignKey('ProcedureDefinition',on_delete=models.CASCADE,blank=True, null=True)
    calibration_date = models.DateTimeField(null=True, blank=True)
    ambient_temperature = models.FloatField(null=True, blank=True)
    ambient_humidity = models.FloatField(null=True, blank=True) 
