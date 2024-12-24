from django.db import models


class Customer_pichina(models.Model):
    name = models.CharField(db_index=True, unique=True, max_length=128, blank=False, null=False)
    short_name = models.CharField(max_length=32, blank=False, null=False, unique=True)
    # notes = models.ManyToManyField('Note', blank=True)
    contact_name = models.CharField(max_length=32, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    accounting_email = models.EmailField(blank=True, null=True)
    po_required = models.BooleanField(default=False)
    is_pvel = models.BooleanField(blank=True,null=True)

