import json
import fileinput
import os
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date

from lsdb.models import AvailableDefect
from lsdb.models import Crate
from lsdb.models import Customer
from lsdb.models import Disposition
from lsdb.models import Group
from lsdb.models import Location
from lsdb.models import MeasurementDefinition
from lsdb.models import ModuleProperty
from lsdb.models import ModuleTechnology
from lsdb.models import Note
from lsdb.models import PlexusImport
from lsdb.models import ProcedureDefinition
from lsdb.models import ProcedureResult
from lsdb.models import Project
from lsdb.models import Unit
from lsdb.models import StepDefinition
from lsdb.models import TestSequenceDefinition
from lsdb.models import UnitType
from lsdb.models import UnitTypeFamily
from lsdb.models import UserProfile
from lsdb.models import UserRegistrationStatus
from lsdb.models import WorkOrder


class Command(BaseCommand):
    help = 'Loads users from json into lsdb'
    oids = {}
    types ={}
    counts = {}

    me = User.objects.get(pk=1)
    project_group = Group.objects.get(name='Projects')
    placeholder = Disposition.objects.get(name='Placeholder disposition')
    unit_type_family = UnitTypeFamily.objects.get(name="Solar Module")
    default_tech = ModuleTechnology.objects.get(name="Mono-PERC")
    location = Location.objects.get(name='BKL')
    crate = Crate.objects.get(pk=1)
    lsdb = apps.get_app_config('lsdb')
    auth = apps.get_app_config('auth')

    try:
        # KLUGE: bad data workarounds
        ModuleTechnology.objects.create(name="c-Si")
        ModuleTechnology.objects.create(name="p-Si")
        ModuleTechnology.objects.create(name="poly-Si")
        ModuleTechnology.objects.create(name="CIGS")
        ModuleTechnology.objects.create(name="CIS")
    except:
        pass

    def handle(self, *args, **options):
        # insert the users and grab their oids
        self.load_users()
        self.load_defects()
        self.load_customers()
        #
        # # Reconstruct deleted record:
        try:
            cust = Customer.objects.get(name="Hanwha Q-Cells")
            self.store_oid(
                        plexus_oid = '57702fe9342817162d0119c0',
                        user = self.me,
                        lsdb_model = 'customer',
                        lsdb_id = cust.id
                    )
        except IntegrityError:
            pass

        self.load_crates()
        self.load_projects()
        self.load_types()
        self.load_modules()
        # self.load_diode()
        # self.load_visual() # TODO
        # self.load_leakage() # TODO
        # self.load_crate_images() # TODO
        # self.load_defect_images() # TODO
        # self.get_counts()

    def store_oid(self, **kwargs):
        imported_oid = PlexusImport.objects.create(
            plexus_oid = kwargs.get('plexus_oid'),
            user = kwargs.get('user'),
            lsdb_model = kwargs.get('lsdb_model'),
            lsdb_id = kwargs.get('lsdb_id'),
        )
        return imported_oid

    def get_oid(self, **kwargs):
        plexus_oid = PlexusImport.objects.get(plexus_oid=kwargs.get('plexus_oid'))
        if plexus_oid.lsdb_model == 'user':
            model = self.auth.get_model('user')
        else:
            model = self.lsdb.get_model(plexus_oid.lsdb_model)
        return model.objects.get(pk=plexus_oid.lsdb_id)

    def load_diode(self):
        points={}
        skipped =0
        self.counts['DiodeTest']=0
        test_sequence_definition = TestSequenceDefinition.objects.get(name='Extra Characterizations')
        procedure_definition = ProcedureDefinition.objects.get(name='Diode Test')
        step_definition = StepDefinition.objects.get(name='Test Diode')
        pass_fail = MeasurementDefinition.objects.get(name='Diode Test Pass/Fail')
        forward_voltage = MeasurementDefinition.objects.get(name='Forward Voltage')
        reverse_voltage = MeasurementDefinition.objects.get(name='Reverse Voltage')

        with fileinput.input(files=('./lsdb/fixtures/loader/DiodeTest.json')) as f:
            for line in f:
                obj = json.loads(line)
                points[obj.get('characterizationPoint')] = self.counts['DiodeTest']
                try:
                    # self.oids[obj.get('_id')['$oid']] = object
                    unit = self.oids.get(obj.get('moduleUnderTest').get('$oid'))
                    print(unit)
                    procedure_result = ProcedureResult.objects.create(
                        unit = unit,
                        procedure_definition = procedure_definition,
                        disposition = self.placeholder,
                        work_order = unit.workorder_set()[0],
                        linear_execution_group = 0,
                        name = obj.get('characterizationPoint'),
                        group = self.project_group,
                        test_sequence_definition = test_sequence_definition,
                    )
                    print(procedure_result)
                    step_result = StepResult.objects.create(
                        procedure_result = procedure_result,
                        step_definition = step_definition,
                        disposition = self.placeholder,
                        name = step_definition.name,
                        step_type = step_definition.step_type,
                        linear_execution_group = 0,
                    )
                    print(step_result)
                    # pass_fail = MeasurementResult.objects.create(
                    #     step_result = step_result,
                    #     measurement_definition =
                    # )
                    # forward_voltage = MeasurementResult.objects.create(
                    #
                    # )
                    # reverse_voltage = MeasurementResult.objects.create(
                    #
                    # )
                    self.counts['DiodeTest'] += 1
                except Exception as e:
                    print('{} {}'.format(e.args, e))
                    # print(obj)
        # print(points)
        print('{} DiodeTest loaded, {} skipped'.format(self.counts['DiodeTest'],skipped))


    def load_modules(self):
        skipped =0
        self.counts['PVModule'] =0
        with fileinput.input(files=('./lsdb/fixtures/loader/PVModule.json')) as f:
            for line in f:
                obj = json.loads(line)
                id = obj.get('_id')
                try:
                    plexus_oid = self.get_oid(plexus_oid=id['$oid'])
                    skipped +=1
                    print('skipping')
                    continue
                except ObjectDoesNotExist:
                    pass
                try:
                    if obj.get('originalCrate'):
                        crate = self.get_oid(plexus_oid=obj.get('originalCrate').get("$oid"))
                    else:
                        crate = self.crate
                    object = Unit.objects.create(
                        unit_type = self.get_oid(plexus_oid=obj.get('moduleType').get("$oid")),
                        crate = crate,
                        serial_number = obj.get('serialNumber'),
                        location = self.location,
                    )

                    if obj.get('quote'):
                        # Cowardly not creating Work Orders without a project
                        if obj.get('BOM'):
                            try:
                                work_order = WorkOrder.objects.get(
                                    name=obj.get('BOM'),
                                    project=self.get_oid(plexus_oid=obj.get('quote').get('$oid'))
                                )
                            except ObjectDoesNotExist:
                                work_order = WorkOrder.objects.create(
                                    name = obj.get('BOM'),
                                    project = self.get_oid(plexus_oid=obj.get('quote').get('$oid')),
                                    disposition = self.placeholder,
                                )
                            work_order.units.add(object)
                        self.get_oid(plexus_oid=obj.get('quote').get('$oid')).units.add(object)
                        plexus_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                            lsdb_model = 'unit',
                            lsdb_id = object.id
                        )
                    self.counts['PVModule'] += 1
                except Exception as e:
                    skipped +=1
                    print(e)
                    print(obj)
        print('{} modules loaded, {} skipped'.format(self.counts['PVModule'],skipped))


    def load_projects(self):
        skipped = 0
        self.counts['Quote'] = 0
        with fileinput.input(files=('./lsdb/fixtures/loader/Quote.json')) as f:
            for line in f:
                obj = json.loads(line)
                id = obj.get('_id')
                try:
                    plexus_oid = self.get_oid(plexus_oid=id['$oid'])
                    skipped +=1
                except ObjectDoesNotExist:
                    try:
                        object = Project.objects.create(
                            number = obj.get('name'),
                            customer = self.get_oid(plexus_oid= obj.get("customer")["$oid"]),
                            project_manager = self.me,
                            group=self.project_group,
                            disposition = self.placeholder,
                            # start_date = obj.get('created_on')['$date'],
                        )
                        plexus_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                            lsdb_model = 'project',
                            lsdb_id = object.id
                        )
                        self.counts['Quote'] +=1
                    except IntegrityError:
                        # need to deduplicate these too...
                        object = Project.objects.get(
                            number = obj.get('name'),
                            group=self.project_group,
                        )
                        plexus_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                            lsdb_model = 'project',
                            lsdb_id = object.id
                        )

        print('{} projects loaded, {} skipped'.format(self.counts['Quote'],skipped))

    def load_crates(self):
        skipped =0
        self.counts['PVModuleCrate'] = 0
        with fileinput.input(files=('./lsdb/fixtures/loader/PVModuleCrate.json')) as f:
            for line in f:
                obj = json.loads(line)
                id = obj.get('_id')
                try:
                    plexus_oid = self.get_oid(plexus_oid=id['$oid'])
                    skipped +=1
                except ObjectDoesNotExist:
                    try:
                        object = Crate.objects.create(
                            name = obj.get('name'),
                            disposition = self.placeholder,
                            shipped_by = self.get_oid(plexus_oid=obj.get("shippedBy")["$oid"])
                        )
                        crate_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                            lsdb_model = 'crate',
                            lsdb_id = object.id
                        )
                    except IntegrityError:
                        # deduplicate crate names
                        object = Crate.objects.get(
                            name = obj.get('name'),
                            shipped_by = self.get_oid(plexus_oid=obj.get("shippedBy")["$oid"])
                        )
                        crate_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                            lsdb_model = 'crate',
                            lsdb_id = object.id
                        )
                    try:
                        self.counts['PVModuleCrate'] +=1
                        # Notes children can be created now, photos, need special handling
                        for observation in obj.get('observations'):
                            if observation.get('photo'):
                                # TODO: This will be handled in a separate pass
                                # print(observation)
                                pass
                            if observation.get('comment'):
                                note_id = observation.get('_id')
                                note = Note.objects.create(
                                    user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                                    subject = "Observation Comment",
                                    text = observation.get('comment'),
                                    datetime = obj.get('created on')['$date'],
                                )
                                object.observations.add(note)
                                object.save()
                                note_oid = self.store_oid(
                                    plexus_oid = note_id['$oid'],
                                    user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                                    lsdb_model = 'note',
                                    lsdb_id = note.id
                                )
                    except IntegrityError as e:
                        print(e)
                        self.oids[obj.get('_id')['$oid']] = Crate.objects.get(name = obj.get('name'),
                                shipped_by = self.oids[obj.get("shippedBy")["$oid"]])
                        # skipped +=1
                    # print(e)
        print('{} crates loaded, {} skipped'.format(self.counts['PVModuleCrate'],skipped))

    def load_types(self):
        skipped =0
        self.counts['PVModuleType'] = 0
        with fileinput.input(files=('./lsdb/fixtures/loader/PVModuleType.json')) as f:
            for line in f:
                obj = json.loads(line)
                id = obj.get('_id')
                try:
                    plexus_oid = self.get_oid(plexus_oid=id['$oid'])
                    skipped +=1
                    continue
                except ObjectDoesNotExist:
                    try:
                        # get a unique moduleType to see if it exists before blindly making another one:
                        # print(obj.get('manufacturer').get('$oid'))
                        # mfr_oid = obj.get('manufacturer').get('$oid')
                        object = UnitType.objects.get(
                            model = obj.get('modelNumber'),
                            manufacturer = self.get_oid(plexus_oid=obj.get('manufacturer').get('$oid'))
                        )
                        # put the oid in:
                        plexus_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                            lsdb_model = 'unittype',
                            lsdb_id = object.id
                        )
                        continue
                    except ObjectDoesNotExist:
                        pass #?
                try:
                    mod_props = ModuleProperty.objects.create(
                        number_of_cells = obj.get('cellData',{'cellsInSeries':0}).get('cellsInSeries',0),
                        nameplate_pmax = obj.get('nameplateData',{'pmax':0}).get('pmax',0),
                        module_width = obj.get('moduleDimensions',{'width':0}).get('width',0),
                        module_height = obj.get('moduleDimensions',{'height':0}).get('height',0),
                        system_voltage = obj.get('systemVoltage',0),
                        module_technology = self.default_tech,
                        isc = obj.get('nameplateData',{'isc':0}).get('isc',0),
                        voc = obj.get('nameplateData',{'voc':0}).get('voc',0),
                        imp = obj.get('nameplateData',{'imp':0}).get('imp',0),
                        vmp = obj.get('nameplateData',{'vmp':0}).get('vmp',0),
                    )
                    if obj.get('cellData'):
                        module_technology = ModuleTechnology.objects.get(name = obj.get('cellData').get('cellType',"Mono-PERC"))
                        mod_props.cells_in_series = obj.get('cellData').get('cellsInSeries',0)
                        mod_props.cells_in_parallel = obj.get('cellData').get('cellsInParallel',0)
                        mod_props.cell_area = obj.get('cellData').get('cellArea',0)
                        mod_props.save()
                    if obj.get('temperatureCoefficients'):
                        mod_props.alpha_isc = obj.get('temperatureCoefficients').get('alphaIsc',0)
                        mod_props.beta_voc = obj.get('temperatureCoefficients').get('betaVoc',0)
                        mod_props.amma_pmp = obj.get('temperatureCoefficients').get('gammaPmax',0)
                        mod_props.save()
                    object = UnitType.objects.create(
                        model = obj.get('modelNumber'),
                        manufacturer = self.get_oid(plexus_oid=obj.get('manufacturer').get('$oid')),
                        unit_type_family = self.unit_type_family,
                        module_property = mod_props,
                    )
                    plexus_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.get_oid(plexus_oid=obj.get("created by")["$oid"]),
                            lsdb_model = 'unittype',
                            lsdb_id = object.id
                    )
                    self.counts['PVModuleType'] +=1
                except Exception as e:
                    print(e)
                    skipped +=1
        print('{} Types loaded, {} skipped'.format(self.counts['PVModuleType'],skipped))

    def load_users(self):
        count = 0
        skipped = 0
        status = UserRegistrationStatus.objects.get(status="New User")
        with fileinput.input(files=('./lsdb/fixtures/loader/plexus_users.json')) as f:
            for line in f:
                obj = json.loads(line)
                id = obj.get('_id')
                try:
                    plexus_oid = self.get_oid(plexus_oid=id['$oid'])
                    skipped +=1
                except ObjectDoesNotExist:
                    user = User.objects.create(
                        username = obj.get('email'),
                        is_active=True,
                        first_name =obj.get('first name'),
                        last_name = obj.get('last name'),
                    )
                    user.set_password('solar123')
                    user.save()
                    UserProfile.objects.create(
                        user=user,
                        notes = id['$oid'],
                        user_registration_status=status,
                        )
                    plexus_oid = self.store_oid(
                        plexus_oid = id['$oid'],
                        user = self.me,
                        lsdb_model = 'user',
                        lsdb_id = user.id
                    )
                    count +=1
        print('{} users loaded, {} skipped'.format(count,skipped))

    def load_defects(self):
        count = 0
        skipped = 0
        self.counts['PVVisualInspectionDefect'] = 0
        with fileinput.input(files=('./lsdb/fixtures/loader/PVVisualInspectionDefect.json')) as f:
            for line in f:
                obj = json.loads(line)
                id = obj.get('_id')
                try:
                    plexus_oid = self.get_oid(plexus_oid=id['$oid'])
                    skipped +=1
                except ObjectDoesNotExist:
                    try:
                        object = AvailableDefect.objects.create(
                            category = obj.get('category'),
                            description = obj.get('description'),
                            short_name = obj.get('shortName'),
                        )
                    except IntegrityError:
                        try:
                            defect = AvailableDefect.objects.get(category=obj.get('category'), short_name=obj.get('shortName'))
                            plexus_oid = self.store_oid(
                                plexus_oid = id['$oid'],
                                user = self.me,
                                lsdb_model = 'availabledefect',
                                lsdb_id = defect.id
                            )
                        except IntegrityError:
                            pass
                    count +=1
        print('{} defects loaded, {} skipped'.format(count,skipped))


    def load_customers(self):
        skipped =0
        self.counts['Corporation'] = 0
        with fileinput.input(files=('./lsdb/fixtures/loader/Corporation.json')) as f:
            for line in f:
                obj = json.loads(line)
                type = obj.get('__t')
                id = obj.get('_id')
                try:
                    plexus_oid = self.get_oid(plexus_oid=id['$oid'])
                    skipped +=1
                except ObjectDoesNotExist:
                    try:
                        object = Customer.objects.create(
                            name = obj.get('name')
                        )
                    except IntegrityError:
                        # this deduplicates while maintaining all references to the single
                        object = Customer.objects.get(
                            name = obj.get('name')
                        )
                        plexus_oid = self.store_oid(
                            plexus_oid = id['$oid'],
                            user = self.me,
                            lsdb_model = 'customer',
                            lsdb_id = object.id
                        )
                    self.counts['Corporation'] +=1
        print('{} customers loaded, {} skipped'.format(self.counts['Corporation'],skipped))

    def get_counts(self): # stubbed
        # dump record counts for the lulz
        with fileinput.input(files=('./lsdb/fixtures/loader/plexus_usermgds.json')) as f:
            for line in f:
                obj = json.loads(line)
                type = obj.get('__t')

                type_count = self.types.get(type)
                if type_count:
                    self.types[type] += 1
                else:
                    self.types[type] = 1

        for type in self.types.keys():
            print('{} : {} / {}'.format(type, self.types[type],
                self.counts.get(type,0)
                ))
