from django.db import models

class RetestProcedures(models.Model):
    retestreason = models.ForeignKey('RetestReasons', on_delete=models.CASCADE,null=True, blank=True)
    procedure_result = models.ForeignKey('ProcedureResults', on_delete=models.CASCADE,null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
