from django.db import models

class StepResultNotes(models.Model):
    notes = models.CharField(max_length=500, blank=True, null=True)
    step_result = models.ForeignKey('StepResult', on_delete=models.CASCADE, blank=False, null=False)
    username = models.CharField(max_length=32, blank=True, null=True)
    datetime = models.DateTimeField(blank=True,null=True)
    procedure_result= models.ForeignKey('ProcedureResult', on_delete=models.CASCADE, blank=True, null=True)
    is_active=models.BooleanField(null=False)
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, blank=True, null=True)
    asset_name = models.CharField(max_length=100, blank=True, null=True)