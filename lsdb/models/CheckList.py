from django.db import models 

class CheckList(models.Model):
    category = models.CharField(max_length=150,null=True,blank=True)
    check_point = models.TextField(null=True,blank=True)