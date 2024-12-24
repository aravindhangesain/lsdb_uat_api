from django.db import models


class ModuleIntakeDetails_pichina(models.Model):
    location = models.ForeignKey('Location_pichina', on_delete=models.CASCADE, blank=False, null=False)
    lot_id = models.CharField(max_length=128,blank=True, null=True)
    projects = models.ForeignKey('Project_pichina', on_delete=models.CASCADE, blank=False, null=False)
    customer = models.ForeignKey('Customer_pichina', on_delete=models.CASCADE, blank=False, null=False)
    bom = models.CharField(max_length=128, blank=True, null=True)
    module_type = models.CharField(max_length=128, blank=True, null=True)
    number_of_modules = models.IntegerField(blank=True, null=True)
    steps = models.CharField(max_length=128, blank=True, null=True)
    is_complete = models.BooleanField(max_length=128, blank=True, null=True)
    intake_date = models.DateTimeField(blank=True,null=True)
    received_date = models.DateTimeField(blank=True,null=True)
    intake_by = models.CharField(max_length=128, blank=True, null=True)
    newcrateintake = models.ForeignKey('NewCrateIntake_pichina', on_delete=models.CASCADE, blank=False, null=False)
    