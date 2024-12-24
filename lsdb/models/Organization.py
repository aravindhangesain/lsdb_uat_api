from django.db import models

class Organization(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)

    class Meta:
        ordering = ('name',)
        unique_together = ['name',] # This solves the serial number collision issue
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
