from django.db import models


class ProjectModifiedDetails(models.Model):
    modified_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    modified_on = models.DateField(auto_now=True)
    role = models.CharField(max_length=32, blank=True, null=True)
    number = models.CharField(max_length=32, blank=False, null=False)
    comments = models.CharField(max_length=150, blank= True, null = True )
