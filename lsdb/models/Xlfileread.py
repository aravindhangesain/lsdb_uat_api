from django.db import models

class xlfileread(models.Model):
    serialnumber = models.CharField(max_length=90, null=True, blank=True)
    projectnumber = models.CharField(max_length=90, null=True, blank=True)
    customername = models.CharField(max_length=90, null=True, blank=True)
    workorder = models.CharField(max_length=90, null=True, blank=True)
    location = models.CharField(max_length=90, null=True, blank=True)


