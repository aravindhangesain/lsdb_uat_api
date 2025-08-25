from django.db import models

class ReportChecklistData(models.Model):
    report = models.ForeignKey('ReportResult', on_delete=models.CASCADE, null=True, blank=True)
    checklist = models.ForeignKey('CheckList', on_delete=models.CASCADE)
    checklist_report = models.ForeignKey('ChecklistReport', on_delete=models.CASCADE, null=True, blank=True )
    status = models.BooleanField(default=False)