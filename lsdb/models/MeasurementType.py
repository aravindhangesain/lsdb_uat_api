from django.db import models



class MeasurementType(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False, unique=True, db_index=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    order_by = models.IntegerField(blank=False, null=False)
    # out_of_family_limit = models.ForeignKey('OutOfFamilyLimit', on_delete=models.CASCADE, blank=True, null=True)
    limit = models.ForeignKey('Limit', on_delete=models.CASCADE, blank=False, null=False)
    parent_measurement_type = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    measurement_result_type = models.ForeignKey('MeasurementResultType', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "{} ({})".format(self.name, self.description)
