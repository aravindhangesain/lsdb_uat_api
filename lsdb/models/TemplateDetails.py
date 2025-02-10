from django.db import models


class TemplateDetails(models.Model):
    template_relations=models.CharField(max_length=256, blank=True, null=True)
    template_master=models.ForeignKey('TemplateMaster', on_delete=models.CASCADE, blank=False, null=False)
    temp_modified_date=models.DateTimeField(blank=True, null=True)
    column1=models.CharField(max_length=256, blank=True, null=True)
    column2=models.CharField(max_length=256, blank=True, null=True)
    column3=models.CharField(max_length=256, blank=True, null=True)