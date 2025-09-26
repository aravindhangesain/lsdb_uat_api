from django.db import models

class AssetSubAsset(models.Model):
    asset=models.ForeignKey('AssetCalibration',on_delete=models.CASCADE,related_name='asset_calibration', blank=True, null=True)
    sub_asset=models.ForeignKey('AssetCalibration',on_delete=models.CASCADE, blank=True, null=True)
    linked_date=models.DateTimeField(null=True, blank=True)