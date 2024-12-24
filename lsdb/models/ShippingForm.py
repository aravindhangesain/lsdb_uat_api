from django.db import models


class ShippingForm(models.Model):
    factory_name=models.CharField(max_length=500,null=True,blank=True)
    factory_address=models.CharField(max_length=500,null=True,blank=True)
    client_name=models.CharField(max_length=500,null=True,blank=True)
    client_address=models.CharField(max_length=500,null=True,blank=True)
    client_contactor=models.CharField(max_length=500,null=True,blank=True)
    client_tel=models.BigIntegerField(null=True)
    customer=models.ForeignKey('Customer', on_delete=models.CASCADE, blank=False, null=False)
    pi_contactor=models.CharField(max_length=500,null=True,blank=True)
    pi_tel=models.BigIntegerField(null=True)
    pi_address=models.CharField(max_length=500,null=True,blank=True)
