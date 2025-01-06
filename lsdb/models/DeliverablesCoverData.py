from django.db import models

class DeliverablesCoverData(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=True, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, blank=True, null=True)
    workorder = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, blank=True, null=True)
    contact_name = models.CharField(max_length=254, blank=True, null=True)
    contact_email = models.CharField(max_length=254, blank=True, null=True)
    revision = models.CharField(max_length=254, blank=True, null=True)
    status = models.CharField(max_length=254, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    classification = models.CharField(max_length=254, blank=True, null=True)
    author = models.ForeignKey('auth.User', related_name='deliverables_authored', on_delete=models.CASCADE, blank=True, null=True)
    checked = models.ForeignKey('auth.User', related_name='deliverables_checked', on_delete=models.CASCADE, blank=True, null=True)
    approved = models.ForeignKey('auth.User', related_name='deliverables_approved', on_delete=models.CASCADE, blank=True, null=True)
    provided_by = models.CharField(max_length=254, blank=True, null=True)
    title = models.CharField(max_length=254, blank=True, null=True)

