from django.db import models

class ProjectFactoryWitness(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    factory_witness = models.BooleanField(default=False)

    
        