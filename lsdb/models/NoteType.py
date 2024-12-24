from django.db import models

from lsdb.models import Group

class NoteType(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    visible_name = models.CharField(max_length=128, blank=True, null=True)
    description = models.CharField(max_length=128, blank=True, null=True)
    groups = models.ManyToManyField("Group", blank=True)

    class Meta:
        ordering = ('name',)
    def __str__(self):
        return "{}".format(self.name)
