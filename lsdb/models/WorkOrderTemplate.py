from django.db import models


class WorkOrderTemplate(models.Model):


    
    workorder=models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=False, null=False)
    template_name=models.CharField(max_length=128, blank=True, null=True)


