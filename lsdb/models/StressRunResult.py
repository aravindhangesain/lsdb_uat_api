from django.db import models


class StressRunResult(models.Model):
    run_name = models.CharField(max_length=255, null=True, blank=True)
    step_result = models.ForeignKey('StepResult', on_delete=models.CASCADE, related_name='stress_run_results')
    asset=models.ForeignKey('AssetCalibration', on_delete=models.CASCADE, related_name='stress_run_results')
    user=models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='stress_run_done_by')
    run_date=models.DateTimeField()
    comment=models.CharField(max_length=255, null=True, blank=True)
    procedure_result=models.ForeignKey('ProcedureResult', on_delete=models.CASCADE, related_name='stress_run_results', null=True, blank=True)
    stress_name=models.CharField(max_length=255, null=True, blank=True)
    disposition=models.ForeignKey('Disposition',on_delete=models.CASCADE,null=True, blank=True)
    is_calibrated=models.BooleanField(null=False,blank=False)


