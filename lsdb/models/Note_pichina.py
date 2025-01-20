from django.db import models


class Note_pichina(models.Model):
    user = models.ForeignKey('AuthUser_pichina', on_delete=models.CASCADE)
    subject = models.CharField(max_length=256, blank=False, null=False)
    text = models.TextField(blank=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=False, null=True,
        default=16)
    note_type = models.ForeignKey('Notetype_pichina', on_delete=models.CASCADE, blank=False, null=False,
        default=1)
    parent_note = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    # organization = models.ForeignKey('Organization', on_delete=models.CASCADE, blank=False, null=False,
    #     default=1) # For the future
    owner = models.ForeignKey('AuthUser_pichina', related_name='noteowner', on_delete=models.CASCADE, blank=True, null=True)
    # attachments = models.ManyToManyField('AzureFile_pichina', blank=True)
    # groups = models.ManyToManyField('Group_pichina', blank=True)
    # labels = models.ManyToManyField('Label', blank=True)
    tagged_users = models.ManyToManyField('AuthUser_pichina', related_name='notetaggedusers', blank=True)
    # read_status = models.ManyToManyField('AuthUser_pichina', related_name='notereadstaus', through='NoteReadStatus', blank=True)
    # text_content markdown/text

    class Meta:
        ordering = ('user','subject',)
    def __str__(self):
        return "{}".format(self.subject)
