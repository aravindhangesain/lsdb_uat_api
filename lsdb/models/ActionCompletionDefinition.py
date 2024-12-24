from django.db import models

'''
this is going to hold all of the critera for an action to be marked "Done"
User scenarios:
    I want to mark an action done manually (no-criteria)
    -- the action has no entiries in the criteria column
    I want the system to compare two columns for equality
    I want the system to compare a number of records to a %

'''
class ActionCompletionDefinition(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    plugin_name = models.CharField(max_length=256, blank=False, null=False)
    # Not sure of this yet, but the model could be like a json and references to things like self.
    plugin_params = models.CharField(max_length=256, blank=False, null=False)
    expected_result = models.BooleanField(blank=False, null=False)

    class Meta:
        unique_together = ['name',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
