from django.db import models

class FeedBackFiles(models.Model):
    feedbackios = models.ForeignKey('FeedBackIOS', on_delete=models.CASCADE, db_column='feedbackios_id',related_name='feedback_files')
    azurefile = models.ForeignKey('AzureFile', on_delete=models.CASCADE, db_column='azurefile_id')

    def __str__(self):
        return f"Feedback ID: {self.feedbackios.id}, File ID: {self.azurefile.id}"