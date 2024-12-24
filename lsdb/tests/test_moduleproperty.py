from django.test import TestCase
from datetime import datetime
import uuid

from lsdb.models import ModuleTechnology as ModuleTechnology
from lsdb.models import ModuleProperty as ModuleProperty

# Create your tests here.
class ModuleTecnologyTestCase(TestCase):
    def setUp(self):
        self.date = datetime.today().date()
        self.slug = str(uuid.uuid4()).split('-')[0]
        self.moduletechnology = ModuleTechnology.objects.create(
            name = 'mt_name-{}'.format(self.slug),
            description = 'mt_desc-{}'.format(self.slug)
        )

    def test_moduleproperty_create(self):
        """ ModuleProperty object create """
        moduleproperty = ModuleProperty.objects.create(
            number_of_cells = 144,
            nameplate_pmax =320.20,
            module_width = 99.99,
            module_height = 88.99,
            system_voltage = 350.35,
            module_technology = self.moduletechnology,
            auditor = 'auditor-{}'.format(self.slug),
            audit_date = self.date,
            audit_report_id = 'ar_id-{}'.format(self.slug),
        )

        self.assertEqual(moduleproperty.number_of_cells, 144)
        self.assertEqual(moduleproperty.nameplate_pmax, 320.20)
        self.assertEqual(moduleproperty.module_width, 99.99)
        self.assertEqual(moduleproperty.module_height, 88.99)
        self.assertEqual(moduleproperty.system_voltage, 350.35)
        self.assertEqual(moduleproperty.module_technology, self.moduletechnology)
        self.assertEqual(moduleproperty.auditor, 'auditor-{}'.format(self.slug))
        self.assertEqual(moduleproperty.audit_date, self.date)
        self.assertEqual(moduleproperty.audit_report_id, 'ar_id-{}'.format(self.slug))

        self.assertEqual(moduleproperty.module_technology.name, 'mt_name-{}'.format(self.slug))
        self.assertEqual(self.moduletechnology.moduleproperty_set.all()[0].number_of_cells, 144)
