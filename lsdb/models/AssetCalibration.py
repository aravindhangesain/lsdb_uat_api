from django.db import models

class AssetCalibration(models.Model):
    asset=models.ForeignKey('Asset',on_delete=models.CASCADE, blank=False, null=True)
    asset_number = models.CharField(max_length=150, blank=True, null=False)
    asset_name = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    last_action_datetime = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey('Location',on_delete=models.CASCADE,blank=False, null=False)
    manufacturer = models.CharField(max_length=150, blank=True, null=True)
    usage = models.CharField(max_length=150, blank=True, null=True)
    model = models.CharField(max_length=150, blank=True, null=True)
    serial_number = models.CharField(max_length=150, blank=False, null=False)
    is_calibration_required = models.BooleanField(null=False)
    last_calibrated_date = models.DateTimeField(null=True,blank=True)
    schedule_for_calibration = models.IntegerField(null=True,blank=True)
    external_asset_required= models.BooleanField(null=True,blank=True)
    asset_type = models.ForeignKey('AssetType',on_delete=models.CASCADE, blank=False, null=True)
    azurefile = models.ForeignKey('AzureFile',on_delete=models.CASCADE, blank=False, null=True)