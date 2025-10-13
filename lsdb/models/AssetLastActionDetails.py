from django.db import models


class AssetLastActionDetails(models.Model):
    asset = models.ForeignKey('AssetCalibration', on_delete=models.CASCADE, blank=True, null=True)
    action_name=models.CharField(max_length=120, blank=True, null=True)
    action_datetime=models.DateTimeField(blank=True, null=True)
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=True, null=True)