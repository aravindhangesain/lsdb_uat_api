from django.db import models

class FeedBackIOS(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    fb_file = models.ForeignKey('AzureFile',on_delete=models.CASCADE,db_column='fb_file_id')
    comments = models.CharField(max_length=250, blank=True, null=True)
    fb_type = models.CharField(max_length=250, blank=False, null=False)
    priority = models.CharField(max_length=250, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    



