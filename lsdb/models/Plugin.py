from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
from lsdb.models import Disposition
from lsdb.models import Group

class Plugin(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=256, blank=False, null=False, unique=True) # db_index provided by unique=True
    description = models.CharField(max_length=256, blank=False, null=False)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    reviewed_by_user = models.ForeignKey('auth.User', related_name='plugin_reviewed_by_user', on_delete=models.CASCADE, blank=True, null=True)
    review_datetime = models.DateTimeField(blank=True, null=True)
    revision = models.IntegerField(default=1, blank=False, null=False)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=False, null=False)
    source_code = models.TextField(blank=True, null=True)
    byte_code = models.TextField(blank=True, null=True)
    restricted = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)
    def __str__(self):
        return "{}".format(self.name)
