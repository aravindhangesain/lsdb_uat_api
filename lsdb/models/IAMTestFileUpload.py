from datetime import datetime
from django.db import models

class IAMTestFileUpload(models.Model):
    file_path = models.FileField()
    serial_number = models.CharField(max_length=255,blank=True, null=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)