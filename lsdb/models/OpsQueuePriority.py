from django.db import models



class OpsQueuePriority(models.Model):
    procedure_result=models.ForeignKey('ProcedureResult', on_delete=models.CASCADE, blank=False, null=False)
    unit=models.ForeignKey('Unit', on_delete=models.CASCADE, blank=False, null=False)
    created_date=models.DateTimeField(blank=True, null=True)
    status=models.BooleanField(blank=True, null=True)
