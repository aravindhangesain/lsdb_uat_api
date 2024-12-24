from django.db import models

class GroupType(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        ordering = ('name',)
        unique_together = ['name',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
