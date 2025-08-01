from django.db import models

class NewFlashTestDetails(models.Model):
    serial_number = models.CharField(max_length=150,null=True,blank=True)
    date_time = models.DateTimeField(null=True,blank=True)
    json_file = models.CharField(max_length=150,null=True,blank=True)
    json_file_path = models.CharField(max_length=150,null=True,blank=True)
    pdf_file = models.CharField(max_length=150,null=True,blank=True)
    pdf_file_path = models.CharField(max_length=150,null=True,blank=True)