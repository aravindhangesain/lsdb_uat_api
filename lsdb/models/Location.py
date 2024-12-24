from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False, unique=False)
    description = models.CharField(max_length=128, blank=False, null=False)
    parent_location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='child_locations', blank=True, null=True)

    class Meta:
        ordering = ('name',)
        unique_together = ['name','parent_location']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
