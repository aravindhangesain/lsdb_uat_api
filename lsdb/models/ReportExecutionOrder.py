from django.db import models


class ReportExecutionOrder(models.Model):
    execution_group_name=models.CharField(max_length=256, blank=True, null=True)
    report_definition=models.ForeignKey('ReportTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    product_definition=models.ForeignKey('ProductTypeDefinition', on_delete=models.CASCADE, blank=False, null=False)
    execution_group_number = models.FloatField()
    report_sequence_definition=models.ForeignKey('ReportSequenceDefinition', on_delete=models.CASCADE, blank=False, null=False)
    
