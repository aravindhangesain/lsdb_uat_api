from django.db import models
from lsdb.models import Disposition

class DispositionCode(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False, unique=True)
    dispositions = models.ManyToManyField('Disposition', blank=True)

    class Meta:
        ordering = ('name',)
        # unique_together = ['asset_type','name','location']
        # indexes = [
        #     models.Index(fields=unique_together)
        # ]

    def __str__(self):
        return "{}".format(self.name)
