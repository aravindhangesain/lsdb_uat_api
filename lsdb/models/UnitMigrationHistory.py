from django.db import models
from datetime import datetime

class UnitMigrationHistory(models.Model):
    initial_serial_number = models.CharField(max_length=128, blank=True, null=True)
    initial_project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True,related_name='initial_project')
    initial_workorder = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=True, null=True,related_name='initial_workorder')
    migrated_serial_number = models.CharField(max_length=128, blank=True, null=True)
    migrated_project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True,related_name='migrated_project')
    migrated_workorder = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=True, null=True,related_name='migrated_workorder')
    migration_date = models.DateTimeField(default=datetime.now)
    migrated_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True,related_name='migration_user')