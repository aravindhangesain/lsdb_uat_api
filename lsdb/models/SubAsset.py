from django.db import models


class SubAsset(models.Model):
    sub_asset_name=models.CharField(max_length=32, blank=True, null=True, unique=True)
    description=models.CharField(max_length=128, blank=True, null=True)
    last_calibrated_date=models.DateTimeField(blank=True, null=True)
    next_calibration=models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name