from django.db import models


class WorkOrderUpdateHistory(models.Model):
    work_order=models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=False, null=False)
    datetime=models.DateField(blank=True, null=True)
    done_by=models.ForeignKey('auth.User', blank=False, null=False, on_delete=models.CASCADE)
    disposition=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)