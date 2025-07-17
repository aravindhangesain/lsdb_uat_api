from django.db import models

class ReportNoteLabels(models.Model):
    label =models.ForeignKey('Label', on_delete=models.CASCADE, null=True, blank=True)
    reportnote = models.ForeignKey('ReportNotes', on_delete=models.CASCADE, null=True, blank=True)