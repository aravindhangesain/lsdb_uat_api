from django.db import models

from django.contrib.auth.models import User
from lsdb.models import Note
from datetime import datetime

class NoteReadStatus(models.Model):
    read_datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User',related_name='notereaduser', on_delete=models.CASCADE)
    note = models.ForeignKey('Note', on_delete=models.CASCADE)

    class Meta:
        unique_together =['user','note']
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.execution_group_number)
