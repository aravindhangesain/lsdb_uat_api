from django.db import models


class Group_pichina(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    notes = models.CharField(max_length=128, blank=True, null=True)
    # organization = models.ForeignKey('Organization', on_delete=models.CASCADE, blank=False, null=False)
    # group_type = models.ForeignKey('GroupType', on_delete=models.CASCADE, blank=False, null=False)
    unit_type = models.ManyToManyField('UnitType_pichina', blank=True)
    # users = models.ManyToManyField('auth.User', blank=True)

    class Meta:
        ordering = ('name',)
        unique_together = ['name',]  # This solves the serial number collision issue
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.name)
