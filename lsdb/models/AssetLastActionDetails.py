from django.db import models


class AssetLastActionDetails(models.Model):
    asset = models.ForeignKey('AssetCalibration', on_delete=models.CASCADE, blank=True, null=True)
    action_name=models.CharField(max_length=120, blank=True, null=True)
    action_datetime=models.DateTimeField(blank=True, null=True)
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True)
    notes=models.CharField(max_length=300, blank=True, null=True)
    status=models.CharField(max_length=100, blank=True, null=True)
    verified_by=models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='verified_by',blank=True, null=True)
    requested_last_calibrated_date=models.DateTimeField(blank=True, null=True)
    requested_schedule_for_calibration=models.IntegerField(null=True,blank=True)