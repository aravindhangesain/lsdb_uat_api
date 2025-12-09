from django.db import models

class NewFlashTestPoints(models.Model):
    serial_number = models.CharField(max_length=128, blank=True, null=True)
    procedure_result = models.ForeignKey('ProcedureResult', on_delete=models.CASCADE, blank=True, null=True)
    v_oc_raw = models.FloatField(blank=True, null=True)
    v_oc_corr = models.FloatField(blank=True, null=True)
    kappa = models.FloatField(blank=True, null=True)
    sweep_type = models.CharField(max_length=64, blank=True, null=True)
    spectral_mismatch = models.FloatField(blank=True, null=True)
    unit_type = models.ForeignKey('UnitType', on_delete=models.CASCADE, blank=True, null=True)
