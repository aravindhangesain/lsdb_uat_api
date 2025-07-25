from django.db import models

class ReportNotes(models.Model):
    report = models.ForeignKey('ReportResult',on_delete=models.CASCADE,null=True,blank=True)
    subject = models.CharField(max_length=256, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    type =  models.ForeignKey('NoteType',on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    datetime = models.DateTimeField(auto_now_add=True)
    reviewer = models.ForeignKey('ReportTeam',on_delete=models.CASCADE,null=True,blank=True)
    labels = models.ManyToManyField('Label',blank=True)
    tagged_pm = models.ManyToManyField('auth.User',related_name = 'reportnotetaggedprojectmanager',blank=True)
    parent_note = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)