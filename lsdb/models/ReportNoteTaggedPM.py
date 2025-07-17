from django.db import models

class ReportNoteTaggedPM(models.Model):
    project_manager =models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    reportnote = models.ForeignKey('ReportNotes', on_delete=models.CASCADE, null=True, blank=True)