from django.db import models

class UserRegistrationStatus(models.Model):
    status = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        ordering = ('status',)
        unique_together = ['status',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.status)
