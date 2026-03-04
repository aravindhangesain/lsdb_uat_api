from django.db import models
from datetime import datetime

class UnitMigrationHistory(models.Model):
    initial_serial_number = models.CharField(max_length=128, blank=False, null=False)
    initial_project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=False, null=False)
    initial_workorder = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=False, null=False)
    migrated_serial_number = models.CharField(max_length=128, blank=False, null=False)
    migrated_project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=False, null=False)
    migrated_workorder = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=False, null=False)
    migration_date = models.DateTimeField(default=datetime.now)
    migrated_by = models.ForeignKey('User', on_delete=models.CASCADE, blank=False, null=False)