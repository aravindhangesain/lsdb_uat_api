from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
from lsdb.models import NoteType
from lsdb.models import AzureFile
from lsdb.models import Label
from lsdb.models import Disposition
from lsdb.models import NoteReadStatus
from lsdb.models import Organization

class Note(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    subject = models.CharField(max_length=256, blank=False, null=False)
    text = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=True,
        default=16)
    note_type = models.ForeignKey('NoteType', on_delete=models.CASCADE, blank=False, null=False,
        default=1)
    parent_note = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, blank=False, null=False,
        default=1) # For the future
    owner = models.ForeignKey('auth.User', related_name='noteowner', on_delete=models.CASCADE, blank=True, null=True)
    attachments = models.ManyToManyField('AzureFile', blank=True)
    groups = models.ManyToManyField('Group', blank=True)
    labels = models.ManyToManyField('Label', blank=True)
    tagged_users = models.ManyToManyField('auth.User', related_name='notetaggedusers', blank=True)
    read_status = models.ManyToManyField('auth.User', related_name='notereadstaus', through='NoteReadStatus', blank=True)
    # text_content markdown/text

    class Meta:
        ordering = ('user','subject',)
    def __str__(self):
        return "{}".format(self.subject)
