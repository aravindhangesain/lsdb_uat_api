from django.db import models


class MeasurementResultResultFilesPichina(models.Model):
    measurement_result = models.ForeignKey('MeasurementResult_pichina', on_delete=models.CASCADE,db_column='measurementresult_id')
    azure_file = models.ForeignKey('AzureFile_pichina',on_delete=models.CASCADE,db_column='azurefile_id')

    class Meta:
        db_table = 'lsdb_measurementresult_result_files_pichina'
        managed = False  