from django.db import models

class xlupload(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    last_action_datetime = models.DateTimeField(auto_now=True)
    disposition = models.ForeignKey('Disposition', on_delete=models.CASCADE, blank=False, null=False)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=False, null=False)