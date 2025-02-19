from django.db import models



class FinalProcedure(models.Model):

    selected_procedure=models.IntegerField(blank=True, null=True)
    procedure=models.IntegerField(blank=True, null=True)

