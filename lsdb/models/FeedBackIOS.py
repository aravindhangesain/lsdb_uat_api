from django.db import models

class FeedBackIOS(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='feedback_ios')
    comments = models.CharField(max_length=250, blank=True, null=True)
    fb_type = models.CharField(max_length=250, blank=False, null=False)
    priority = models.CharField(max_length=250, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    



