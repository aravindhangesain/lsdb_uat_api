from django.db import models

from datetime import datetime

class Permission(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)
    permission_types = models.ManyToManyField('PermissionType', blank=True) # POST, GET, etc.
    permitted_views = models.ManyToManyField('PermittedView', blank=True)

    class Meta:
        ordering = ('name','group',)
        unique_together =['name','group']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
