from django.db import models


class ProjectTemplate(models.Model):
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True)
    template_name = models.CharField(max_length=128, blank=True, null=True)