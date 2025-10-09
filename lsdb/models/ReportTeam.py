from django.db import models

class ReportTeam(models.Model):
    report_type = models.ForeignKey('ReportTypeDefinition', on_delete=models.CASCADE, null=True, blank=True)
    reviewer = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    writer = models.ForeignKey('auth.User', related_name='writer', on_delete=models.CASCADE, null=True, blank=True)
    approver = models.ForeignKey('auth.User', related_name='approver', on_delete=models.CASCADE, null=True, blank=True)
    is_projmanager = models.BooleanField(default=False)
    duration = models.IntegerField(null=True, blank=True)
    reviewer_pm = models.BooleanField(default=False)
    