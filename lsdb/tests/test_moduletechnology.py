from django.test import TestCase
import uuid

from lsdb.models import ModuleTechnology as ModuleTechnology

# Create your tests here.
class ModuleTegnologyTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]

    def test_moduletechnology_create(self):
        """ ModuleTechnology object create """
        moduletechnology = ModuleTechnology.objects.create(
            name = 'name-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug)
        )
        self.assertEqual(moduletechnology.name, 'name-{}'.format(self.slug))
        self.assertEqual(moduletechnology.description, 'desc-{}'.format(self.slug))
