from django.test import TestCase
from datetime import datetime
import uuid

from lsdb.models import Limit
from lsdb.models import LimitComparison
from lsdb.models import LimitComparisonMode
from lsdb.models import SiPrefix

# Create your tests here.
class LimitTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]
        self.now = datetime.today()

        self.limitcmp_one = LimitComparison.objects.create(
            name = 'limitcmp_one-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug),
        )
        self.limitcmp_two = LimitComparison.objects.create(
            name = 'limitcmp_two-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug),
        )
        self.si_prefix = SiPrefix.objects.create(
            name = 'siprefix_name-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug),
        )

        self.limitcmp_mode = LimitComparisonMode.objects.create(
            name = 'limitcmp_mode-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug),
        )
        # MeasurementResult
        # Unit
        # AssetCapacity

    def test_limit_create(self):
        """ Asset object created """
        limit = Limit.objects.create(
            value_boolean = True,
            value_string ='STRING',
            limit_one = 77.77,
            limit_two = 99.99,
            limit_comparison_one= self.limitcmp_one,
            limit_comparison_two= self.limitcmp_two,
            limit_comparison_mode = self.limitcmp_mode,
            precision = 100,
            units= 'grammeters',
            scientific_format =True,
            si_prefix = self.si_prefix,
            choice_of_list = 'choice-{}'.format(self.slug) ,
            case_sensitive_compare_string = True,
        )
        self.assertTrue(limit.value_boolean)
        self.assertTrue(limit.scientific_format)
        self.assertTrue(limit.case_sensitive_compare_string)

        self.assertEqual(limit.value_string, 'STRING')
        self.assertEqual(limit.limit_one, 77.77)
        self.assertEqual(limit.limit_two, 99.99)
        self.assertEqual(limit.precision, 100)
        self.assertEqual(limit.units, 'grammeters')
        self.assertEqual(limit.choice_of_list, 'choice-{}'.format(self.slug))
        self.assertEqual(limit.limit_comparison_one.name,'limitcmp_one-{}'.format(self.slug))
        self.assertEqual(limit.limit_comparison_two.name,'limitcmp_two-{}'.format(self.slug))
        self.assertEqual(limit.limit_comparison_mode.name,'limitcmp_mode-{}'.format(self.slug))
        self.assertEqual(limit.si_prefix.name, 'siprefix_name-{}'.format(self.slug))

        self.assertEqual(self.limitcmp_one.limitcomparisonone.all()[0].choice_of_list, 'choice-{}'.format(self.slug))
        self.assertEqual(self.limitcmp_two.limitcomparisontwo.all()[0].choice_of_list, 'choice-{}'.format(self.slug))
        self.assertEqual(self.limitcmp_mode.limit_set.all()[0].choice_of_list, 'choice-{}'.format(self.slug))
        self.assertEqual(self.si_prefix.limit_set.all()[0].choice_of_list, 'choice-{}'.format(self.slug))
