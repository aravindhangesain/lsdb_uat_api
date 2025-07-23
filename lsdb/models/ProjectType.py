from django.db import models


class ProjectType(models.Model):
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True)
    project_type = models.CharField(max_length=128, blank=True, null=True)