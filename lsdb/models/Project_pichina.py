from django.db import models

class Project_pichina(models.Model):
    # notes = models.ManyToManyField('Note', blank=True)
    # sri_notes = models.ManyToManyField('Note', related_name='sri_notes', blank=True)
    number = models.CharField(max_length=32, blank=False, null=False)
    sfdc_number = models.CharField(max_length=32, blank=True, null=True)
    project_manager = models.ForeignKey('AuthUser_pichina',blank=False, null=False, on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer_pichina', blank=False, null=False, on_delete=models.CASCADE)
    # group = models.ForeignKey('Group_pichina', on_delete=models.CASCADE, blank=False, null=False)
    start_date = models.DateField(blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    disposition = models.ForeignKey('Disposition_pichina', on_delete=models.CASCADE, blank=False, null=False)
    proposal_price = models.FloatField(blank=True, null=True)
    # attachments = models.ManyToManyField('AzureFile', blank=True)
    # actions = GenericRelation('ActionResult')
    is_pvel = models.BooleanField(default=False, null=False, blank=False)
    # location = models.ForeignKey('Location', blank=False, null=True, on_delete=models.CASCADE)
    # unit_disposition = (return/destroy)
    # expected_unit_types = models.ManyToManyField('ExpectedUnitType', blank=True)


    def get_units(self,unit_type):
        from django.db import connection
        query = """
        SELECT unit_id
        FROM lsdb_project_units_pichina pu
        JOIN lsdb_unit_pichina u ON pu.unit_id = u.id
        WHERE pu.project_id = %s
        """
        params = [self.id]
        if unit_type:
            query += " AND u.unit_type_id = %s"
            params.append(unit_type.id)

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

        return [row[0] for row in rows]

