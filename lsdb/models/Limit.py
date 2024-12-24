from django.db import models

from lsdb.models import LimitComparison
from lsdb.models import LimitComparisonMode
from lsdb.models import SiPrefix


class Limit(models.Model):
    # this one is implemented oddly in the reference
    value_boolean = models.BooleanField()
    value_string = models.CharField(max_length=32, blank=True, null=True)
    limit_one = models.FloatField()
    limit_two = models.FloatField()
    limit_comparison_one = models.ForeignKey('LimitComparison', related_name ='limitcomparisonone', on_delete=models.CASCADE, blank=False, null=False)
    limit_comparison_two = models.ForeignKey('LimitComparison', related_name ='limitcomparisontwo', on_delete=models.CASCADE, blank=False, null=False)
    limit_comparison_mode = models.ForeignKey('LimitComparisonMode', on_delete=models.CASCADE, blank=False, null=False)
    precision = models.IntegerField()
    units = models.CharField(max_length=32, blank=False, null=False)
    scientific_format = models.BooleanField()
    si_prefix = models.ForeignKey('SiPrefix', on_delete=models.CASCADE, blank=False, null=False)
    choice_of_list = models.CharField(max_length=32, blank=True, null=True)
    case_sensitive_compare_string = models.BooleanField()


    class Meta:
        # ordering = ('name',)
        unique_together = [
            'value_boolean',
            'value_string',
            'limit_one',
            'limit_two',
            'limit_comparison_one',
            'limit_comparison_two',
            'limit_comparison_mode',
            'precision',
            'units',
            'scientific_format',
            'si_prefix',
            'choice_of_list',
            'case_sensitive_compare_string',
        ]
        indexes = [
            models.Index(fields=unique_together)
        ]

    def __str__(self):
        return "{} {} {} {} to {} significant digits".format(
            self.si_prefix,
            self.units,
            self.limit_comparison_one,
            self.limit_one,
            self.precision,
        )
