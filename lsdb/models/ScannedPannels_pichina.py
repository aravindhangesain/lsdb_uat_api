from django.db import models

class ScannedPannels_pichina(models.Model):
    serial_number = models.CharField(max_length=128, blank=False, null=False)
    test_sequence = models.ForeignKey('TestSequenceDefinition_pichina', on_delete=models.CASCADE, blank=True, null=True)
    status = models.BooleanField()
    module_intake  = models.ForeignKey('ModuleIntakeDetails_pichina', on_delete=models.CASCADE, blank=False, null=False)
    arrival_date= models.DateTimeField(blank=True,null=True)
    project_closeout_date= models.DateTimeField(blank=True,null=True)
    eol_disposition= models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=False, null=True)