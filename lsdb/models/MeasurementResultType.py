from django.db import models

class MeasurementResultType(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False, unique=True, db_index=True)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        ordering = ('name',)
    def __str__(self):
        return "{}".format(self.name)
