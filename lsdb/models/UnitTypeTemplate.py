from django.db import models


class UnitTypeTemplate(models.Model):


    
    unittype=models.ForeignKey('UnitType', on_delete=models.CASCADE, blank=False, null=False)
    template_name=models.CharField(max_length=128, blank=True, null=True)


