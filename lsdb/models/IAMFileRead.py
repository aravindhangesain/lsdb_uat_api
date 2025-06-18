from django.db import models

class IAMFileRead(models.Model):
    unit = models.ForeignKey('Unit',on_delete=models.CASCADE, blank=False, null=False)
    project = models.ForeignKey('Project',on_delete=models.CASCADE, blank=False, null=False)
    customer = models.ForeignKey('Customer',on_delete=models.CASCADE, blank=False, null=False)
    workorder = models.ForeignKey('WorkOrder',on_delete=models.CASCADE, blank=False, null=False)
    datetime = models.DateTimeField(null=True, blank=True)
    led0 = models.FloatField(null=True, blank=True)
    led1 = models.FloatField(null=True, blank=True)
    led2 = models.FloatField(null=True, blank=True)
    led3 = models.FloatField(null=True, blank=True)
    led4 = models.FloatField(null=True, blank=True)
    led5 = models.FloatField(null=True, blank=True)
    led6 = models.FloatField(null=True, blank=True)
    led7 = models.FloatField(null=True, blank=True)



