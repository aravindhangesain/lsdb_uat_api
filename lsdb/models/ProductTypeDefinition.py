from django.db import models


class ProductTypeDefinition(models.Model):
    name=models.CharField(max_length=256, blank=True, null=True)
    linear_execution_order=models.IntegerField(blank=True, null=True)
    group=models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)
    disposition=models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    version=models.CharField(max_length=256, blank=True, null=True)