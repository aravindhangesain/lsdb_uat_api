from django.db import models


class UnitTypeTemplate(models.Model):


    template_name=models.CharField(max_length=250, blank=False, null=False)
    unittype=models.ForeignKey('UnitType', on_delete=models.CASCADE, blank=False, null=False)


