from django.db import models

class AdditionalModuleProperty(models.Model):
    unit_type = models.ForeignKey('UnitType', on_delete=models.CASCADE, blank=True, null=True)
    alpha_stc_correction_a_per_c=models.FloatField(blank=True, null=True)
    beta_stc_correction_v_per_c=models.FloatField(blank=True, null=True)
    kappa_stc_correction_ohm_per_c=models.FloatField(blank=True, null=True)
    r_s_stc_correction_ohm=models.FloatField(blank=True, null=True)
    flash_parameters=models.CharField(max_length=120, blank=True, null=True)