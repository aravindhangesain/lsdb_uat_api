from django.db import models

class StressRunDetails(models.Model):
    stress_run_result = models.ForeignKey('StressRunResult', on_delete=models.CASCADE, related_name='stress_run_details')
    sub_asset = models.ForeignKey('SubAsset', on_delete=models.CASCADE, related_name='stress_run_details')
    