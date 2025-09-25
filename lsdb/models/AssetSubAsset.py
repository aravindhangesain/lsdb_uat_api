from django.db import models

class AssetSubAsset(models.Model):
    asset=models.ForeignKey('Asset',on_delete=models.CASCADE, blank=True, null=True)
    sub_asset=models.ForeignKey('SubAsset',on_delete=models.CASCADE, blank=True, null=True)
    linked_date=models.DateTimeField(null=True, blank=True)