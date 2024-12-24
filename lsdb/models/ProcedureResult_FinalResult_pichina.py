from django.db import models

class ProcedureResult_FinalResult_pichina(models.Model):
    procedure_result = models.ForeignKey('ProcedureResult_pichina',on_delete=models.CASCADE, blank=True, null=True)
    procedure_definition = models.ForeignKey('ProcedureDefinition_pichina',on_delete=models.CASCADE, blank=True, null=True)
    final_result = models.BooleanField()
    updated_date = models.DateTimeField(blank=True, null=True)
    