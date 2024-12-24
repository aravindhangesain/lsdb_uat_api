from django.db import models


class Workorder_pichina(models.Model):
    name = models.CharField(max_length=32, blank=False, null=False)
    description = models.CharField(max_length=128, blank=True, null=True)
    project = models.ForeignKey('Project_pichina', on_delete=models.CASCADE, blank=False, null=False)
    start_datetime = models.DateTimeField(blank=True, null=True) # NTP Date
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    # disposition_codes = models.ManyToManyField('DispositionCode', blank=False)
    test_sequence_definitions = models.ManyToManyField('TestSequenceDefinition_pichina', blank=True, through='TestSequenceExecutionData_pichina')
    tib = models.BooleanField(blank=True, null=True) # "Temporarily Imported under Bond"
    unit_disposition = models.ForeignKey('Disposition_pichina', related_name='unitdisposition',
        on_delete=models.CASCADE, blank=False, null=False, default=23) # recycle after 30 days

    class Meta:
        ordering = ('name',)
        unique_together =['name','project',]
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.name)
    

    def get_units(self):
        from django.db import connection

        query = """
        SELECT unit_id 
        FROM lsdb_workorder_units_pichina 
        WHERE workorder_id = %s
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [self.id])
            rows = cursor.fetchall()
        return [row[0] for row in rows]
