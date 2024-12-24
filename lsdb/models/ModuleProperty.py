from django.db import models
from datetime import datetime

class ModuleProperty(models.Model):
    # this table needs to be normalized into oblivion
    number_of_cells = models.IntegerField(blank=False, null=False)
    nameplate_pmax = models.FloatField(blank=False, null=False)
    module_width = models.FloatField(blank=False, null=False)
    module_height = models.FloatField(blank=False, null=False)
    system_voltage =  models.FloatField(blank=False, null=False)
    module_technology = models.ForeignKey('ModuleTechnology', on_delete=models.CASCADE, blank=False, null=False)
    # auditor info looks optional
    auditor = models.CharField(max_length=32, blank=True, null=True)
    audit_date = models.DateField(blank=True, null=True)
    audit_report_id = models.CharField(max_length=32, blank=True, null=True)
    isc = models.FloatField(blank=False, null=False)
    voc = models.FloatField(blank=False, null=False)
    imp = models.FloatField(blank=False, null=False)
    vmp = models.FloatField(blank=False, null=False)
    alpha_isc = models.FloatField(blank=True, null=True)
    beta_voc =  models.FloatField(blank=True, null=True)
    gamma_pmp =  models.FloatField(blank=True, null=True)
    cells_in_series = models.IntegerField(blank=True, null=True)
    cells_in_parallel = models.IntegerField(blank=True, null=True)
    cell_area = models.FloatField(blank=True, null=True)
    bifacial = models.BooleanField(blank=True, null=True)

    class Meta:
        ordering = ('nameplate_pmax',)

    def __str__(self):
        return "{} Cell {}W {}V {}".format(
            self.number_of_cells,
            self.nameplate_pmax,
            self.system_voltage,
            self.module_technology.name,
            )
