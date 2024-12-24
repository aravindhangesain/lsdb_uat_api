from django.db import models
from django.contrib.auth.models import User


class PlexusImport(models.Model):
    plexus_oid = models.CharField(max_length=64, blank=False, null=False, unique=True)
    lsdb_id = models.IntegerField(blank=False, null=False)
    lsdb_model = models.CharField(max_length=64, blank=True, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        unique_together = ['plexus_oid','lsdb_id','lsdb_model'] # This solves the serial number collision issue
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.plexus_oid)
