from django.db import models

class LocationLog(models.Model):
    location= models.ForeignKey('Location', on_delete=models.CASCADE)
    project= models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True)
    unit=models.ForeignKey('Unit', on_delete=models.CASCADE, blank=True, null=True)
    datetime=models.DateTimeField(null=True,blank=True)
    is_latest=models.BooleanField(null=True,blank=True)
    asset_id=models.IntegerField(null=True,blank=True)
    flag=models.IntegerField(null=True,blank=True)
    username=models.CharField(max_length=128, blank=True, null=True)

