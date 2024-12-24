from django.test import TestCase
from datetime import datetime
import uuid

from lsdb.models import AvailableDefect

# Create your tests here.
class AvailableDefectTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]
        # disposition
        # MeasurementResult
        # Unit
        # AssetCapacity

    def test_available_defect_create(self):
        """ Available Defect object create """
        available_defect = AvailableDefect.objects.create(
            category = 'category-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug)
        )
        self.assertEqual(available_defect.category, 'category-{}'.format(self.slug))
        self.assertEqual(available_defect.description, 'desc-{}'.format(self.slug))
