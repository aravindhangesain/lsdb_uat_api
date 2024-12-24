from django.db import models


class Asset_pichina(models.Model):
    name = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    location = models.ForeignKey('Location_pichina', on_delete=models.CASCADE, blank=False, null=False)
    last_action_datetime = models.DateTimeField(auto_now_add=True)
    # asset_type = models.ForeignKey('AssetType', related_name='obsolete_asset_type', on_delete=models.CASCADE, blank=False, null=False)
    # asset_types = models.ManyToManyField('AssetType', blank=True)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    # notes = models.ManyToManyField('Note', blank=True)

    class Meta:
        ordering = ('name',)
        unique_together = ['name','location']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
