from django.test import TestCase
from datetime import datetime
import uuid

from lsdb.models import Asset
from lsdb.models import AssetCapacity
from lsdb.models import AssetType
from lsdb.models import Disposition
from lsdb.models import Location

# Create your tests here.
class AssetCapacityTestCase(TestCase):
    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]
        self.now = datetime.today()

        # Until I build fixtures...
        self.location = Location.objects.create(
            name = 'location-{}'.format(self.slug),
            description = 'location-desc-{}'.format(self.slug)
        )
        self.asset_type = AssetType.objects.create(
            name = 'asset_type-{}'.format(self.slug),
            description = 'desc-{}'.format(self.slug)
        )
        self.disposition = Disposition.objects.create(
            name = 'disp_name-{}'.format(self.slug),
        )
        self.asset = Asset.objects.create(
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

    def test_asset_capacity_create(self):
        """ AssetCapacity created with Asset """
        asset_capacity = AssetCapacity.objects.create(
            serial_number = 'serial_number-{}'.format(self.slug),
            project_id= 'project_id-{}'.format(self.slug),
            work_order_name= 'work_order_name-{}'.format(self.slug),
            asset = self.asset,
        )
        self.assertEqual(asset_capacity.serial_number, 'serial_number-{}'.format(self.slug))
        self.assertEqual(asset_capacity.project_id, 'project_id-{}'.format(self.slug))
        self.assertEqual(asset_capacity.work_order_name, 'work_order_name-{}'.format(self.slug))
        self.assertEqual(asset_capacity.asset.name, 'name-{}'.format(self.slug))
        self.assertEqual(asset_capacity.asset.asset_type.name, 'asset_type-{}'.format(self.slug))
        self.assertEqual(asset_capacity.asset.disposition.name, 'disp_name-{}'.format(self.slug))
        self.assertEqual(asset_capacity.asset.location.name, 'location-{}'.format(self.slug))

        self.assertEqual(self.asset.assetcapacity_set.all()[0].serial_number, 'serial_number-{}'.format(self.slug))
        self.assertEqual(self.asset_type.asset_set.all()[0].name, 'name-{}'.format(self.slug))
        self.assertEqual(self.disposition.asset_set.all()[0].name, 'name-{}'.format(self.slug))
        self.assertEqual(self.location.asset_set.all()[0].name, 'name-{}'.format(self.slug))
