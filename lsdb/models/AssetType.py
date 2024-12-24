from django.db import models
from datetime import datetime

# This may need overhaul seems off
class AssetType(models.Model):
    name = models.CharField(db_index=True, unique=True, max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    # These are reverse lookups:
    # Assets
    # ProcedureDefinitions
    # StepDefinitions
    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "{}".format(self.name)
