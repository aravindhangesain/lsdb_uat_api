from django.db import models

from lsdb.models import Group

class UnitTypePropertyType(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    value = models.CharField(max_length=32, blank=True, null=True)
    source = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    tag = models.CharField(max_length=32, blank=True, null=True)
    controlled = models.BooleanField(blank=True, null=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)
    # TODO: public Guid ElementId { get; set; } /// Id of element to attach to ?
    # element = models.ForeignKey('', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        ordering = ('name',)
        unique_together =['name','tag']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
