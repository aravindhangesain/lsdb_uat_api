from django.db import models
from lsdb.models import Disposition_pichina

class DispositionCode_pichina(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False, unique=True)
    dispositions = models.ManyToManyField('Disposition_pichina', blank=True)

    class Meta:
        ordering = ('name',)
        # unique_together = ['asset_type','name','location']
        # indexes = [
        #     models.Index(fields=unique_together)
        # ]

    def __str__(self):
        return "{}".format(self.name)
