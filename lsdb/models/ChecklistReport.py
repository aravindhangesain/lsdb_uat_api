from django.db import models


class ChecklistReport(models.Model):
    report_name=models.CharField(max_length=256, blank=True, null=True)
    checklist = models.ManyToManyField('CheckList', blank=True)
