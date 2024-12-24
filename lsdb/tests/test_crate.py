from django.test import TestCase
# from datetime import datetime
import uuid

from lsdb.models import Crate
from lsdb.models import Disposition
from lsdb.models import Customer

class ConditionDefinitionTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]

        # Until I build fixtures...
        self.disposition = Disposition.objects.create(
            name = 'disp_name-{}'.format(self.slug),
        )
        self.customer = Customer.objects.create(
            name = 'cust_name-{}'.format(self.slug)
        )

    def test_condition_definition_create(self):
        """ AssetCapacity created with Asset """
        crate = Crate.objects.create(
            name = 'crate_name-{}'.format(self.slug),
            disposition = self.disposition,
            shipped_by = self.customer,
        )

        self.assertEqual(crate.name,'crate_name-{}'.format(self.slug))
        self.assertEqual(crate.disposition.name,'disp_name-{}'.format(self.slug))
        self.assertEqual(crate.shipped_by.name,'cust_name-{}'.format(self.slug))

        self.assertEqual(self.customer.crate_set.all()[0].name, 'crate_name-{}'.format(self.slug))
        self.assertEqual(self.disposition.crate_set.all()[0].name, 'crate_name-{}'.format(self.slug))
