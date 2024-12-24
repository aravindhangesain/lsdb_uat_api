from django.test import TestCase
# from datetime import datetime
import uuid

from lsdb.models import StepType
from lsdb.models import ConditionDefinition
from lsdb.models import StepDefinition

class ConditionDefinitionTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]
        # self.now = datetime.today()

        # Until I build fixtures...
        self.step_type = StepType.objects.create(
            name = 'step_type-{}'.format(self.slug)
        )
        self.step_definition = StepDefinition.objects.create(
            name = 'step_def-{}'.format(self.slug),
            step_type = self.step_type
        )

    def test_condition_definition_create(self):
        """ AssetCapacity created with Asset """
        condition_definition = ConditionDefinition.objects.create(
            name = 'name-{}'.format(self.slug),
            condition_guid = 'guid-{}'.format(self.slug),
            step_definition = self.step_definition,
        )

        self.assertEqual(condition_definition.step_definition.step_type.name,'step_type-{}'.format(self.slug))
        self.assertEqual(condition_definition.step_definition.name,'step_def-{}'.format(self.slug))

        self.assertEqual(self.step_type.stepdefinition_set.all()[0].name, 'step_def-{}'.format(self.slug))
        self.assertEqual(self.step_definition.conditiondefinition_set.all()[0].name, 'name-{}'.format(self.slug))
        self.assertEqual(self.step_type.stepdefinition_set.all()[0].conditiondefinition_set.all()[0].name, 'name-{}'.format(self.slug))
