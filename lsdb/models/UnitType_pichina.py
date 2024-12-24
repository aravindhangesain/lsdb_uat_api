from django.db import models



class UnitType_pichina(models.Model):
    model = models.CharField(max_length=128, blank=False, null=False)
    bom = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    notes = models.CharField(max_length=128, blank=True, null=True)
    manufacturer = models.ForeignKey('Customer_pichina', on_delete=models.CASCADE, blank=False, null=False)
    # datasheets = models.ManyToManyField('AzureFile_pichina', blank=True)
    # unit_type_family = models.ForeignKey('UnitTypeFamily', on_delete=models.CASCADE, blank=False, null=False)
    module_property = models.ForeignKey('ModuleProperty_pichina', on_delete=models.CASCADE, blank=True, null=True) # TODO: This is invalid for inverters
