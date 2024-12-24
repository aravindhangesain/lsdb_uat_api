from django.db import models

TEMPLATE_FORMATS =[['text','text'],['html','html']]
TRANSPORT_TYPES = [['EMAIL','EMAIL']]

class NotificationQueue(models.Model):
    # KLUGE:
    # Repurposing this queue to be a log and a way to check "if sent since"
    transport = models.CharField(choices=TRANSPORT_TYPES, default='EMAIL', max_length=8)
    recipient = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    subject = models.CharField(db_index=True, max_length=255, blank=True, default='')
    text_body = models.TextField(blank=True, default='')
    html_body = models.TextField(blank=True, default='')
    queued_date = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    class Meta:
        ordering =('queued_date',)

    def __str__(self):
        return "{}".format(self.subject)
