from django.db import models



class UserAssignmentForProcedure(models.Model):
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    procedure_result=models.ForeignKey('ProcedureResult', on_delete=models.CASCADE, blank=False, null=False)
    assigned_on=models.DateTimeField(null=True, blank=True)
    assigned_by=models.ForeignKey('auth.User', on_delete=models.CASCADE,related_name='assigned_by', blank=True, null=True)
    due_on=models.IntegerField(null=True,blank=True)

    
