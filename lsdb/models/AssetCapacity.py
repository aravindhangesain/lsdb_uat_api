from django.db import models
from datetime import datetime
from lsdb.models.Asset import Asset

# This may need overhaul seems off
class AssetCapacity(models.Model):
    # Isn't this a unit serial number?
    serial_number = models.CharField(max_length=32, blank=False, null=False)
    # I think this is supposed to be a FK to Project, but what do I know
    project_id = models.CharField(max_length=32, blank=False, null=False)
    # I think this is supposed to be FK to work order but WTF
    work_order_name = models.CharField(max_length=32, blank=True, null=True)
    # I think this is unneded on the assetCapacity, looks like a reverse lookup
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        ordering = ('serial_number',)
        unique_together = ['serial_number','project_id','asset']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.serial_number)
