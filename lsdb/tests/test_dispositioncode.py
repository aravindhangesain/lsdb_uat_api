from django.test import TestCase
from datetime import datetime
import uuid

from lsdb.models import DispositionCode as DispositionCode

# Create your tests here.
class DispositionCodeTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]

    def test_dispositioncode_create(self):
        """ ModuleProperty object create """
        dispositioncode = DispositionCode.objects.create(
            name = 'name-{}'.format(self.slug),
        )

        self.assertEqual(dispositioncode.name, 'name-{}'.format(self.slug))
