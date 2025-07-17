from django.db import models

class ReportNotes(models.Model):
    report = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    subject = models.CharField(max_length=256, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    type =  models.ForeignKey('NoteType',on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    datetime = models.DateTimeField(null=True,blank=True)
    reviewer = models.ForeignKey('ReportReviewer',on_delete=models.CASCADE,null=True,blank=True)
    labels = models.ManyToManyField('Label',blank=True)
    tagged_pm = models.ManyToManyField('auth.User',related_name = 'reportnotetaggedprojectmanager',blank=True)