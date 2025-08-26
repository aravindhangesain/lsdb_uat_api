from django.db import models

class ReportChecklistNote(models.Model):
    report = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    checklist = models.ForeignKey('CheckList', on_delete=models.CASCADE, null=True, blank=True)
    checklist_report = models.ForeignKey('ChecklistReport', on_delete=models.CASCADE, null=True, blank=True )
    subject = models.CharField(max_length=256, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    parent_note = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)