from rest_framework.test import APITestCase
from rest_framework import status
import json

from django.urls import include, path, reverse

from datetime import datetime
import uuid
from django.contrib.auth.models import User

from lsdb.models import Disposition
from lsdb.models import Project
from lsdb.models import TestSequenceDefinition
from lsdb.models import Unit
from lsdb.models import WorkOrder
from lsdb.models import ProcedureResult

# Create your tests here.
class WorkOrderCreateTestCase(APITestCase):
    # create all the objects that a work order needs to be constructed;
    fixtures = [
        'init',
        'auth',
        'post-auth-init',
        'test',
    ]

    def setUp(self):
        self.slug = str(uuid.uuid4()).split('-')[0]
        self.now = datetime.today()

    def test_work_order_create(self):
        self.assertTrue(self.client.login(username='mdavis', password='solar123'))

        start_count = WorkOrder.objects.count()
        # response = self.client.get('/api/1.0/users/')
        data = {
            "name": 'Test-{}'.format(self.slug),
            "description": 'desc-{}'.format(self.slug),
            "project": '/api/1.0/projects/1/',
            "start_datetime": self.now,
            "units": [
                '/api/1.0/units/6/',
                '/api/1.0/units/7/',
                '/api/1.0/units/8/'
            ],
            "disposition": '/api/1.0/dispositions/1/',
            "test_sequence_definition": '/api/1.0/test_sequence_definitions/1/'
        }
        response = self.client.post('/api/1.0/work_orders/', data, format='json')
        # print(response.content)
        # print(response.data)
        work_order = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkOrder.objects.count(), start_count + 1)
        id = work_order.get('id')
        # print('ID:{}'.format(id))

        # This will fail:
        self.assertEqual(ProcedureResult.objects.count(), 1)
        procedure_result = ProcedureResult.objects.get(pk=1)
        self.assertEqual(procedure_result.work_order.id, id)
        # need to know all of the procedure definitions that are attached
        # to this test sequence:
        self.assertEqual(procedure_result.procedure_definition.id, 1)
        #check for the follow-on objects that should now be created:
        # response = slef.client.get('/api/1.0/procedure_results/')
        # procedure_results = json.loads(response.content)
