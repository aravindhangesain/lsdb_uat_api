# This model is obsolete and is left here for historical reference only
from django.db import models

class OutOfFamilyLimit(models.Model):
    limit_one = models.FloatField()
    limit_two = models.FloatField()

    class Meta:
        # ordering = ('name',)
        unique_together = [
            'limit_one',
            'limit_two',
        ]
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{}".format(self.limit_one)
