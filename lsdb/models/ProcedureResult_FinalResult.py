from django.db import models

class ProcedureResult_FinalResult(models.Model):
    procedure_result = models.ForeignKey('ProcedureResult',on_delete=models.CASCADE, blank=True, null=True)
    procedure_definition = models.ForeignKey('ProcedureDefinition',on_delete=models.CASCADE, blank=True, null=True)
    final_result = models.BooleanField()
    updated_date = models.DateTimeField(blank=True, null=True)
    