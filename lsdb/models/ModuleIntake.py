from django.db import models

class ModuleIntake(models.Model):
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=True, null=True)
    



