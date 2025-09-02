from django.db import models


class StressRunResult(models.Model):
    run_name = models.CharField(max_length=255, null=True, blank=True)
    step_result = models.ForeignKey('StepResult', on_delete=models.CASCADE, related_name='stress_run_results')
    asset=models.ForeignKey('Asset', on_delete=models.CASCADE, related_name='stress_run_results')
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='stress_run_done_by')
    run_date=models.DateTimeField()


