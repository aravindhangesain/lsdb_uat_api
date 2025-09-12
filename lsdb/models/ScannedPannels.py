from django.db import models

class ScannedPannels(models.Model):
    serial_number = models.CharField(max_length=128, blank=False, null=False,unique=True)
    test_sequence = models.ForeignKey('TestSequenceDefinition', on_delete=models.CASCADE, blank=True, null=True)
    status = models.BooleanField()
    module_intake  = models.ForeignKey('ModuleIntakeDetails', on_delete=models.CASCADE, blank=False, null=False)
    arrival_date= models.DateTimeField(blank=True,null=True)
    project_closeout_date= models.DateTimeField(blank=True,null=True)
    eol_disposition= models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=True)