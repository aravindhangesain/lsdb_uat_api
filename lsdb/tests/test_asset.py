from django.test import TestCase
from datetime import datetime
import uuid

from lsdb.models import Asset
from lsdb.models import AssetType
from lsdb.models import Disposition
from lsdb.models import Location

# Create your tests here.
class AssetTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]
        self.now = datetime.today()
        # Need to create AssetType or use known
        self.asset_type = AssetType.objects.create(
            name = 'asset_type-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug)
        )
        self.disposition = Disposition.objects.create(
            name = 'disp_name-{}'.format(self.slug)
        )
        self.location = Location.objects.create(
            name = 'location-{}'.format(self.slug),
            description = 'location-desc-{}'.format(self.slug)
        )
        # MeasurementResult
        # Unit
        # AssetCapacity

    def test_asset_create(self):
        """ Asset object created """
        asset = Asset.objects.create(
            name = 'name-{}'.format(self.slug),
            description =  'description-{}'.format(self.slug),
            location = self.location,
            last_action_datetime = self.now,
            asset_type = self.asset_type,
            disposition = self.disposition,
            # measurement_results
            # units
            # asset_capacities
        )
        self.assertEqual(asset.name, 'name-{}'.format(self.slug))
        self.assertEqual(asset.description, 'description-{}'.format(self.slug))
        self.assertEqual(asset.location.name, 'location-{}'.format(self.slug))
        self.assertEqual(asset.asset_type.name, 'asset_type-{}'.format(self.slug))
        self.assertEqual(asset.disposition.name, 'disp_name-{}'.format(self.slug))

        self.assertEqual(self.disposition.asset_set.all()[0].name, 'name-{}'.format(self.slug))
        self.assertEqual(self.asset_type.asset_set.all()[0].name, 'name-{}'.format(self.slug))
