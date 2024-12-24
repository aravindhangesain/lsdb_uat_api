from django.db import models

from lsdb.models import ActionResult
from lsdb.models import ActionDefinition

# This is our "through" table to store completion status
class ActionCompletionResult(models.Model):
    criteria_completed = models.BooleanField(default=False, null=False, blank=False)
    completed_datetime = models.DateTimeField(null=True, blank=True)
    action_result = models.ForeignKey('ActionResult', on_delete=models.CASCADE)
    action_completion_definition = models.ForeignKey('ActionCompletionDefinition', on_delete=models.CASCADE)

    class Meta:
        unique_together =['action_result','action_completion_definition',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{} : {}".format(self.action_completion_definition,self.criteria_completed)
