from django.db import models



class DeviationHistory(models.Model):
    previous_procedure=models.ForeignKey('ProcedureResult',related_name='previous_procedure', on_delete=models.CASCADE, blank=False, null=False)
    current_procedure=models.ForeignKey('ProcedureResult', related_name='current_procedure',on_delete=models.CASCADE, blank=False, null=False)
    pmp_deviation=models.FloatField(blank=True, null=True)
    voc_deviation=models.FloatField(blank=True, null=True)
    vmp_deviation=models.FloatField(blank=True, null=True)
    isc_deviation=models.FloatField(blank=True, null=True)
    imp_deviation=models.FloatField(blank=True, null=True)
    calculated_on= models.DateTimeField(blank=True,null=True)
    calculated_by=models.ForeignKey('auth.User', on_delete=models.CASCADE, blank=False, null=False)