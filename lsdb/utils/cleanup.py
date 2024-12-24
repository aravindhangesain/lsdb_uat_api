# Collection of tools to speed up manual data repair.

from lsdb.models import Unit, WorkOrder, ProcedureResult, TestSequenceDefinition, StepResult, MeasurementResult
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from lsdb.models import Asset, AssetType, Disposition, Location, ProcedureDefinition
from datetime import datetime
from django.utils.timezone import make_aware, activate, now, get_current_timezone
from time import strptime, strftime, localtime

def scheck(this):
    rows=[]
    for line in this.splitlines():
        rows=line.split()
        try:
            unit = Unit.objects.get(serial_number=rows[0])
            if unit.procedureresult_set.count():
                print('{} {} {}'.format(unit.id,unit.serial_number,unit.procedureresult_set.all()[0].test_sequence_definition.name))
            else:
                print('{} {} OK'.format(unit.serial_number,unit.id))
        except:
            print(line,' not found,','similar: ',Unit.objects.filter(serial_number__icontains=line))


def bench():
    import time
    start = time.perf_counter_ns()
    bench_call()
    end = time.perf_counter_ns()
    print('duration:',end - start)

# This should be overwritten with code to bench in bench()
def bench_call():
    test_unit = {'unit':13243}
    test_unit['test_sequence'] = 27
    unit = Unit.objects.get(id=test_unit.get('unit'))
    test_sequence = TestSequenceDefinition.objects.get(id=test_unit.get('test_sequence'))
    for
    return


def bench_call():
    queryset = ProcedureResult.objects.filter(disposition__isnull=True,
        group__name__iexact='characterizations')\
        .annotate(done_to= Max('unit__procedureresult__linear_execution_group',
            filter=Q(unit__procedureresult__disposition__isnull=False)))
    # queryset = ProcedureResult.objects.filter(disposition__isnull=True)\
    #     .annotate(done_to= Max('unit__procedureresult__linear_execution_group',
    #         filter=Q(unit__procedureresult__disposition__isnull=False)))
    master_data_frame = pd.DataFrame(list(queryset.values(
        'unit__serial_number',
        'test_sequence_definition__name',
        'done_to',
        'linear_execution_group',
        'procedure_definition__name',
        'work_order__project__number',
        'work_order__name',
        'name',
        'allow_skip',
        )))


'''
# this is the date bubblilng code to move measurements to procedure_result start_datetime and end_datetime
tofix = ProcedureResult.objects.filter(Q(disposition__isnull=False),(Q(start_datetime__isnull=True)|Q(start_datetime__isnull=True)))
for result in tofix:
    if result.id not in [45,107082,61176,90,5,9,110550,110551,107453]:
        setdates(result)

@transaction.atomic
def setdates(result):
    if result.start_datetime:
        procedure_start = result.start_datetime # needs to be the earliest step start_datetime
    else:
        procedure_start = datetime(2010,1,1,1, tzinfo=timezone.utc)
    if result.end_datetime:
        procedure_end = result.end_datetime # needs to be the latest step end_datetime
    else:
        procedure_end = datetime(2010,1,1,1, tzinfo=timezone.utc)
    for step in result.stepresult_set.all():
        if step.start_datetime == None and step.disposition != None:
            if step.name == "Test Start" or step.name == "Test End":
                # Start Test and End Test handler
                # these should only have one measurement ever.
                try:
                    first_measurement = step.measurementresult_set.filter(result_datetime__isnull=False).order_by('result_datetime').first().result_datetime
                    last_measurement = step.measurementresult_set.filter(result_datetime__isnull=False).order_by('result_datetime').last().result_datetime
                    # print('Stress: first: {} Last {}'.format(first_measurement, last_measurement))
                except Exception as e:
                    print(result.id)
                    print('!!!! Stress:',e)
            else:
                # All others:
                try:
                    first_measurement = step.measurementresult_set.filter(date_time__isnull=False).order_by('date_time').first().date_time
                    last_measurement = step.measurementresult_set.filter(date_time__isnull=False).order_by('date_time').last().date_time
                    # print('Measurement: first: {} Last {}'.format(first_measurement, last_measurement))
                except Exception as e:
                    print(result.id)
                    print('!!!! :',e)
            duration = last_measurement - first_measurement
            step.start_datetime = first_measurement
            step.duration = duration.total_seconds()/60
            step.save()
            # All steps have been "fixed"
            if result.start_datetime == None and procedure_start < first_measurement:
                procedure_start = first_measurement
            if result.end_datetime == None and procedure_end < last_measurement:
                procedure_end = last_measurement
    print('changed {} start {} to {} and end {} to {}'.format(result.id, result.start_datetime, procedure_start, result.end_datetime, procedure_end))
    result.start_datetime = procedure_start
    result.end_datetime = procedure_end
    result.save()

'''
d 103557 start None to 2021-07-20 04:15:20.720723+00:00 and end None to 2021-07-20 04:19:00.478189+00:00
changed 112516 start None to 2021-08-09 18:18:55.806349+00:00 and end None to 2021-08-09 18:21:02.663404+00:00
changed 45089 start None to 2021-01-28 23:15:44.233313+00:00 and end None to 2021-01-29 15:34:40.544309+00:00
changed 45119 start None to 2021-01-28 22:54:02.241254+00:00 and end None to 2021-01-29 15:27:47.839831+00:00
changed 45134 start None to 2021-01-28 22:09:54.563733+00:00 and end None to 2021-01-28 22:10:11.734535+00:00
changed 45074 start None to 2021-01-28 23:04:59.184887+00:00 and end None to 2021-01-29 15:31:18.923933+00:00
changed 115939 start None to 2021-09-16 20:16:26.976957+00:00 and end None to 2021-09-16 20:16:36.832340+00:00
changed 79213 start None to 2021-03-11 18:40:02.894297+00:00 and end None to 2021-03-11 18:40:30.484172+00:00
changed 113132 start None to 2021-08-18 16:01:02.136642+00:00 and end None to 2021-08-18 16:01:15.236041+00:00
changed 106881 start None to 2021-06-28 23:44:27.159
@transaction.atomic
def validate_stress(this):
    from django.db.models import Q, Max
    from lsdb.models import Asset, Unit
    """
    This action will test if the current unit has any reason to be at the provided asset.
    {
        "asset_name":"DiodeTestFixture_001",
        "procedure_definition":$ID <-- parameter for chamber entry to allow for test selection for qualification of the unit.
    }
    This will verify that there are procedure_result objects with disposition=null for the unit.
    If there are empty procedure_results, it will update the unit's fixture_location to reflect the unit has "checked in" at the valid asset.
    procedure_results are returned in linear_execution_group order.
    It will return the asset object of there are NO results for this unit to fill in at this station's asset_type
    """
    rows=[]
    for line in this.splitlines():
        rows=line.split(',')
        try:
            unit = Unit.objects.get(serial_number=rows[0])
            print(unit)
            asset = Asset.objects.get(name__iexact=rows[1])
            definition = []
        except:
            print(line,' not found,','similar: ',Unit.objects.filter(serial_number__icontains=line))
        if unit.disposition.complete:
            print({'message':'This serial number not in an active disposition. Contact engineering.'})
            continue
        if asset:
            # Check to see if this unit has *any* business at this asset type:
            if (asset.asset_types.filter(id__in=AssetType.objects.filter(proceduredefinition__procedureresult__unit=unit))):
                # Check for virgin module:
                if unit.procedureresult_set.filter(disposition__isnull=False,supersede__isnull=True):
                    # Units "in_progress" can only check in at the current asset:
                    if unit.procedureresult_set.filter(work_in_progress_must_comply=True).exclude(stepresult__measurementresult__asset__name=asset).count():
                        old_asset = unit.fixture_location.name
                        # EXCEPT: When there's more than one asset type ?
                        print({'message':'This serial number marked IN PROGRESS at Asset {}. Contact engineering.'.format(old_asset)})
                        continue
                    # Return the procedure result tree that is next for this asset:
                    procedure_results = unit.procedureresult_set.filter(Q(disposition__isnull=True)|Q(disposition__complete=False))
                    procedure_results = procedure_results.exclude(supersede=True)
                    procedure_results = procedure_results.filter(procedure_definition__asset_types__in=asset.asset_types.all())
                    procedure_results = procedure_results.order_by('linear_execution_group')
                    if definition:
                        procedure_results = procedure_results.filter(procedure_definition__id=definition)
                    # This eliminates all of the procedures that aren't in the same LEG:
                    procedure_results = procedure_results.annotate(done_to= Max('unit__procedureresult__linear_execution_group',
                        filter=Q(unit__procedureresult__disposition__isnull=False, unit__procedureresult__supersede__isnull=True)))
                    for result in procedure_results:
                        if (result.done_to > result.linear_execution_group ) or (result.done_to < result.linear_execution_group -1):
                            procedure_results = procedure_results.exclude(id=result.id)
                else:
                    procedure_results = unit.procedureresult_set.filter(procedure_definition__asset_types__in=asset.asset_types.all())
                    procedure_results = procedure_results.order_by('linear_execution_group')
                    first_leg = procedure_results.first().linear_execution_group
                    procedure_results = procedure_results.filter(linear_execution_group=first_leg)
                # TODO: Change such that step order execution is preserved.
                for result in procedure_results:
                    print('{} {} {} {} {}'.format(unit.id,unit.serial_number,result.test_sequence_definition.name,result.procedure_definition.name,result.name))


# Dislike this and it doesn't work so... repurposing. It will force a new empty bucket into
# the given leg_name and leg_number of the unit sequence attached to tsd_id for procedure_definition_id
# insert_procedure('serial_number,tsd_id,leg_name,leg_number,procedure_definition_id,allow_skip')
# insert_procedure('A08201000100210,13,Light Soak >30 kWh/m²,2,16,False')
@transaction.atomic
def insert_procedure(this):
    cols=[]
    errors=[]
    for line in this.splitlines():
        cols=line.split(',')
        try:
            unit=Unit.objects.get(serial_number=cols[0])
        except Exception as e:
            errors.append(
                    "Error: {} Serial: {}".format(e, cols[0])
            )
        try:
            tsd = TestSequenceDefinition.objects.get(id=cols[1])
        except Exception as e:
            errors.append(
                    "Error: {} TSD_ID: {}".format(e, cols[1])
            )
        try:
            work_order = unit.workorder_set.first()
            if not work_order:
                errors.append(
                    "Error: workorder not found for unit {}".format(cols[0])
                )
        except Exception as e:
            errors.append(
                    "Error: looking for workorder {}".format(e)
            )
        try:
            procedure = tsd.procedure_definitions.filter(procedureexecutionorder__procedure_definition__id=cols[4]).first()
        except Exception as e:
            errors.append(
                    "Error: {} ProcedureDefinition: {}".format(e, cols[4])
            )
        if not procedure: # I think this is fatal now
            errors.append(
                "Error: ProcedureDefinition with ID: {} not found-- Fatal".format(cols[4])
            )
            print(errors)
            raise RuntimeError('FATAL')
        else:
            try:
                _build_procedure_bucket(unit,tsd,procedure,work_order,cols[2],cols[3],cols[5])
            except Exception as e:
                errors.append(
                    "Error: creating bucket {} Fatal".format(e)
                )
                print(errors)
                raise RuntimeError('FATAL')

@transaction.atomic
def _build_procedure_bucket(unit, tsd, procedure_definition,work_order,leg_name, leg_num, allow_skip):
    new_result = ProcedureResult.objects.create(
        unit= unit,
        procedure_definition= procedure_definition,
        work_order= work_order,
        linear_execution_group= leg_num,
        name= leg_name,
        group= tsd.group,
        version= tsd.version,
        test_sequence_definition= tsd,
        allow_skip= allow_skip,
    )
    for step_execution in procedure_definition.stepexecutionorder_set.all():
        step_result = StepResult.objects.create(
            name = step_execution.execution_group_name,
            procedure_result = new_result,
            step_definition = step_execution.step_definition,
            execution_number = 0,
            disposition = None,
            start_datetime = None,
            duration = 0,
            test_step_result = None,
            archived = False,
            description = None,
            step_number = 0,
            step_type = step_execution.step_definition.step_type,
            linear_execution_group = step_execution.execution_group_number,
            allow_skip = step_execution.allow_skip,
        )
        for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
            measurement_result = MeasurementResult.objects.create(
                step_result = step_result,
                measurement_definition = measurement_definition,
                software_revision = 0.0,
                disposition = None,
                limit = measurement_definition.limit,
                station = 0,
                name = measurement_definition.name,
                record_only = measurement_definition.record_only,
                allow_skip = measurement_definition.allow_skip,
                requires_review = measurement_definition.requires_review,
                measurement_type = measurement_definition.measurement_type,
                order = measurement_definition.order,
                report_order = measurement_definition.report_order,
                measurement_result_type = measurement_definition.measurement_result_type,
            )

# This will add a new empty procedure_result object into the test plan that is an empty copy
# of the ID specified. Used to create epty retest records after a reassignment
@transaction.atomic
def clone_empty_result(this):
    errors=[]
    try:
        result = ProcedureResult.objects.get(id=this)
    except:
        errors.append(
                "Error: requested procedure result {} does not exist".format()
        )
        return Response(errors)
    test_sequence = TestSequenceDefinition.objects.get(id=result.test_sequence_definition.id)
    procedures = test_sequence.procedureexecutionorder_set.filter(
        execution_group_number = result.linear_execution_group,
        procedure_definition = result.procedure_definition
    )
    if procedures.count() != 1:
        print(
                "Error: requested procedure test definition {} incorrect.".format(test_sequence.id),
                " {} procedures returned, should only ever be 1".format(procedures.count())
            )
        return
    execution = procedures.first()
    try:
        new_result = ProcedureResult.objects.create(
            unit= result.unit,
            procedure_definition= result.procedure_definition,
            work_order= result.work_order,
            linear_execution_group= result.linear_execution_group,
            name= result.name,
            group= result.group,
            version= result.version,
            test_sequence_definition= result.test_sequence_definition,
            allow_skip= result.allow_skip,
        )
        for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
            print(execution)
            step_result = StepResult.objects.create(
                name = step_execution.execution_group_name,
                procedure_result = result,
                step_definition = step_execution.step_definition,
                execution_number = 0,
                disposition = None,
                start_datetime = None,
                duration = 0,
                test_step_result = None,
                archived = False,
                description = None,
                step_number = 0,
                step_type = step_execution.step_definition.step_type,
                linear_execution_group = step_execution.execution_group_number,
                allow_skip = step_execution.allow_skip,
            )
            for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                measurement_result = MeasurementResult.objects.create(
                    step_result = step_result,
                    measurement_definition = measurement_definition,
                    software_revision = 0.0,
                    disposition = None,
                    limit = measurement_definition.limit,
                    station = 0,
                    name = measurement_definition.name,
                    record_only = measurement_definition.record_only,
                    allow_skip = measurement_definition.allow_skip,
                    requires_review = measurement_definition.requires_review,
                    measurement_type = measurement_definition.measurement_type,
                    order = measurement_definition.order,
                    report_order = measurement_definition.report_order,
                    measurement_result_type = measurement_definition.measurement_result_type,
                )
        # result.delete()
    except Exception as e:
        print(e)

@transaction.atomic
def replace_procedure(this):
    errors=[]
    try:
        result = ProcedureResult.objects.get(id=this)
    except:
        errors.append(
                "Error: requested procedure result {} does not exist".format(params.get('procedure_result'))
        )
        return Response(errors)
    test_sequence = TestSequenceDefinition.objects.get(id=result.test_sequence_definition.id)
    procedures = test_sequence.procedureexecutionorder_set.filter(
        execution_group_number = result.linear_execution_group,
        procedure_definition = result.procedure_definition
    )
    if procedures.count() != 1:
        print(
                "Error: requested procedure test definition {} incorrect.".format(test_sequence.id),
                " {} procedures returned, should only ever be 1".format(procedures.count())
            )
        return
    execution = procedures.all()[0]
    try:
        procedure_result = ProcedureResult.objects.create(
            unit = result.unit,
            name = execution.execution_group_name,
            disposition = None,
            group = execution.procedure_definition.group,
            work_order = result.work_order,
            procedure_definition = execution.procedure_definition,
            version = execution.procedure_definition.version,
            linear_execution_group = execution.execution_group_number,
            test_sequence_definition = test_sequence,
            allow_skip = execution.allow_skip,
        )
        for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
            step_result = StepResult.objects.create(
                name = step_execution.execution_group_name,
                procedure_result = procedure_result,
                step_definition = step_execution.step_definition,
                execution_number = 0,
                disposition = None,
                start_datetime = None,
                duration = 0,
                test_step_result = None,
                archived = False,
                description = None,
                step_number = 0,
                step_type = step_execution.step_definition.step_type,
                linear_execution_group = step_execution.execution_group_number,
                allow_skip = step_execution.allow_skip,
            )
            for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                measurement_result = MeasurementResult.objects.create(
                    step_result = step_result,
                    measurement_definition = measurement_definition,
                    software_revision = 0.0,
                    disposition = None,
                    limit = measurement_definition.limit,
                    station = 0,
                    name = measurement_definition.name,
                    record_only = measurement_definition.record_only,
                    allow_skip = measurement_definition.allow_skip,
                    requires_review = measurement_definition.requires_review,
                    measurement_type = measurement_definition.measurement_type,
                    order = measurement_definition.order,
                    report_order = measurement_definition.report_order,
                    measurement_result_type = measurement_definition.measurement_result_type,
                )
        result.delete()
    except Exception as e:
        print(e)


@transaction.atomic
def letid_replace(this):
    errors=[]
    try:
        result = ProcedureResult.objects.get(id=this)
    except:
        errors.append(
                "Error: requested procedure result {} does not exist".format(params.get('procedure_result'))
        )
        return Response(errors)
    test_sequence = TestSequenceDefinition.objects.get(id=result.test_sequence_definition.id)
    procedure = ProcedureDefinition.objects.get(id=13)
    procedures = test_sequence.procedureexecutionorder_set.filter(
        execution_group_number = result.linear_execution_group,
        procedure_definition = procedure
    )
    if procedures.count() != 1:
        print(
                "Error: requested procedure test definition {} incorrect.".format(test_sequence.id),
                " {} procedures returned, should only ever be 1".format(procedures.count())
            )
        return
    execution = procedures.all()[0]
    try:
        procedure_result = ProcedureResult.objects.create(
            unit = result.unit,
            name = execution.execution_group_name,
            disposition = None,
            group = execution.procedure_definition.group,
            work_order = result.work_order,
            procedure_definition = execution.procedure_definition,
            version = execution.procedure_definition.version,
            linear_execution_group = execution.execution_group_number,
            test_sequence_definition = test_sequence,
            allow_skip = execution.allow_skip,
        )
        for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
            step_result = StepResult.objects.create(
                name = step_execution.execution_group_name,
                procedure_result = procedure_result,
                step_definition = step_execution.step_definition,
                execution_number = 0,
                disposition = None,
                start_datetime = None,
                duration = 0,
                test_step_result = None,
                archived = False,
                description = None,
                step_number = 0,
                step_type = step_execution.step_definition.step_type,
                linear_execution_group = step_execution.execution_group_number,
                allow_skip = step_execution.allow_skip,
            )
            for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                measurement_result = MeasurementResult.objects.create(
                    step_result = step_result,
                    measurement_definition = measurement_definition,
                    software_revision = 0.0,
                    disposition = None,
                    limit = measurement_definition.limit,
                    station = 0,
                    name = measurement_definition.name,
                    record_only = measurement_definition.record_only,
                    allow_skip = measurement_definition.allow_skip,
                    requires_review = measurement_definition.requires_review,
                    measurement_type = measurement_definition.measurement_type,
                    order = measurement_definition.order,
                    report_order = measurement_definition.report_order,
                    measurement_result_type = measurement_definition.measurement_result_type,
                )
        result.delete()
    except Exception as e:
        print(e)

@transaction.atomic
def build_bucket(work_order, test_sequence, unit):
    for execution in test_sequence.procedureexecutionorder_set.all():
        # print(procedure.procedureexecutionorder_set.all()[0])
        procedure_result = ProcedureResult.objects.create(
            unit = unit,
            name = execution.execution_group_name,
            disposition = None,
            group = execution.procedure_definition.group,
            work_order = work_order,
            procedure_definition = execution.procedure_definition,
            version = execution.procedure_definition.version,
            linear_execution_group = execution.execution_group_number,
            test_sequence_definition = test_sequence,
            allow_skip = execution.allow_skip,
        )
        for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
            step_result = StepResult.objects.create(
                name = step_execution.execution_group_name,
                procedure_result = procedure_result,
                step_definition = step_execution.step_definition,
                execution_number = 0,
                disposition = None,
                start_datetime = None,
                duration = 0,
                test_step_result = None,
                archived = False,
                description = None,
                step_number = 0,
                step_type = step_execution.step_definition.step_type,
                linear_execution_group = step_execution.execution_group_number,
                allow_skip = step_execution.allow_skip,
            )
            for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                measurement_result = MeasurementResult.objects.create(
                    step_result = step_result,
                    measurement_definition = measurement_definition,
                    software_revision = 0.0,
                    disposition = None,
                    limit = measurement_definition.limit,
                    station = 0,
                    name = measurement_definition.name,
                    record_only = measurement_definition.record_only,
                    allow_skip = measurement_definition.allow_skip,
                    requires_review = measurement_definition.requires_review,
                    measurement_type = measurement_definition.measurement_type,
                    order = measurement_definition.order,
                    report_order = measurement_definition.report_order,
                    measurement_result_type = measurement_definition.measurement_result_type,
                )

def wipe_tests(this):
    unit = Unit.objects.get(serial_number=this)
    for result in unit.procedureresult_set.all():
        print(result)
        result.delete()

# this is how I found all of the problem children:
'''
results = ProcedureResult.objects.all()
definitions ={}
for result in results:
    print('.', end='')
    for step in result.stepresult_set.all():
        execution = StepExecutionOrder.objects.filter(
            procedure_definition__testsequencedefinition__procedureexecutionorder__execution_group_number = result.linear_execution_group,
            procedure_definition__testsequencedefinition__procedureexecutionorder__test_sequence = result.test_sequence_definition,
            procedure_definition = result.procedure_definition,
            step_definition = step.step_definition,
            execution_group_number = step.linear_execution_group).distinct()
        if execution.count() > 1:
            definitions[result.procedure_definition.id] = 1
        if execution.count == 1:
            print(result.test_sequence_definition.id,result.test_sequence_definition.name,
                result.procedure_definition.id, step.name, exstep.execution_group_name)
            print(step.name, execution[0].execution_group_name)
        if execution.count ==0:
            print('0',step.name)
print(definitions)
'''
@transaction.atomic
def lid_assign(serials):
    # Takes a multi-line string of serial_number and destination test sequence
    rows=[]
    for line in serials.splitlines():
        row = line.split(' ')
        if len(row) >= 2:
            try:
                unit=Unit.objects.get(serial_number=row[0])
            except:
                print('unit with serial number {} not found'.format(row[0]))
                continue
            try:
                new_tsd = TestSequenceDefinition.objects.get(id=row[1])
            except:
                print('test sequence definition id {} not found'.format(row[1]))
                continue
            work_order = unit.procedureresult_set.first().work_order
            old_tsd = unit.procedureresult_set.first().test_sequence_definition
            # clean out all empty procedure records:
            for result in unit.procedureresult_set.filter(
                    disposition__isnull = True,
                    stepresult__disposition__isnull = True,
                    stepresult__measurementresult__disposition__isnull = True
                ).distinct():
                print(result)
                result.delete()
            if unit.procedureresult_set.count():
                old_results = unit.procedureresult_set.filter(
                    test_sequence_definition = old_tsd,
                )
                # add the unit to the new test sequence
                build_bucket(work_order,new_tsd, unit)
                for old_result in old_results:
                    if old_result.supersede == True:
                        print('old_result:',old_result.name, old_result.linear_execution_group,old_result.procedure_definition.name,
                            'NOT MOVED')
                        continue
                    print('old_result START')
                    new_results = list(unit.procedureresult_set.filter(
                        test_sequence_definition = new_tsd,
                        disposition__isnull = True,
                        stepresult__disposition__isnull = True,
                        stepresult__measurementresult__disposition__isnull = True
                        ).order_by('linear_execution_group'))
                    for new_result in new_results: # This fails when collapsing the same sequence
                        if new_result.procedure_definition == old_result.procedure_definition and \
                            new_result.linear_execution_group == old_result.linear_execution_group: # New and different bug!
                            print('old_result:',old_result.name, old_result.linear_execution_group,old_result.procedure_definition.name,
                                'new_result:',new_result.name, new_result.linear_execution_group,new_result.procedure_definition.name)
                            old_result.test_sequence_definition = new_tsd
                            old_result.linear_execution_group = new_result.linear_execution_group
                            old_result.name = new_result.name
                            old_result.save()
                            new_result.delete()
                            break
            else:
                build_bucket(work_order,new_tsd, unit)
#
# lid_assign('''TZEAE129-000023 3
# TZEAE129-000002 3
# ''')
@transaction.atomic
def append_test(serials):
    # Takes a multi-line string of serial_number and appending test sequence
    rows=[]
    for line in serials.splitlines():
        row = line.split(' ')
        if len(row) >= 2:
            try:
                unit=Unit.objects.get(serial_number=row[0])
            except:
                print('unit with serial number {} not found'.format(row[0]))
                continue
            try:
                new_tsd = TestSequenceDefinition.objects.get(id=row[1])
            except:
                print('test sequence definition id {} not found'.format(row[1]))
                continue
            work_order = unit.procedureresult_set.first().work_order
            last_leg = unit.procedureresult_set.last().linear_execution_group
            # start adding new procedures with a new LEG starting point
            for execution in new_tsd.procedureexecutionorder_set.all():
                procedure_result = ProcedureResult.objects.create(
                    unit = unit,
                    name = execution.execution_group_name + ' (APPENDED)',
                    disposition = None,
                    group = execution.procedure_definition.group,
                    work_order = work_order,
                    procedure_definition = execution.procedure_definition,
                    version = execution.procedure_definition.version,
                    linear_execution_group = execution.execution_group_number + last_leg,
                    test_sequence_definition = new_tsd,
                    allow_skip = execution.allow_skip,
                )
                for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
                    step_result = StepResult.objects.create(
                        name = step_execution.execution_group_name,
                        procedure_result = procedure_result,
                        step_definition = step_execution.step_definition,
                        execution_number = 0,
                        disposition = None,
                        start_datetime = None,
                        duration = 0,
                        test_step_result = None,
                        archived = False,
                        description = None,
                        step_number = 0,
                        step_type = step_execution.step_definition.step_type,
                        linear_execution_group = step_execution.execution_group_number,
                        allow_skip = step_execution.allow_skip,
                    )
                    for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                        measurement_result = MeasurementResult.objects.create(
                            step_result = step_result,
                            measurement_definition = measurement_definition,
                            software_revision = 0.0,
                            disposition = None,
                            limit = measurement_definition.limit,
                            station = 0,
                            name = measurement_definition.name,
                            record_only = measurement_definition.record_only,
                            allow_skip = measurement_definition.allow_skip,
                            requires_review = measurement_definition.requires_review,
                            measurement_type = measurement_definition.measurement_type,
                            order = measurement_definition.order,
                            report_order = measurement_definition.report_order,
                            measurement_result_type = measurement_definition.measurement_result_type,
                        )


# one off import from a list of serials:
def slap_unit(serials):
    uut = UnitType.objects.get(id=1012)
    work_order = WorkOrder.objects.get(id=574)
    location = Location.objects.get(id=1)
    crate = Crate.objects.get(id=1)
    project = Project.objects.get(id=498)
    rows=[]
    for line in serials.splitlines():
        rows=line.split()
        this = rows[0]
        unit=Unit.objects.create(
            serial_number=this,
            unit_type=uut,
            location=location,
            crate=crate
        )
        unit.workorder_set.add(work_order)
        unit.project_set.add(project)
        print(unit.id)

@transaction.atomic
def remove_stress(serials):
    rows=[]
    for line in serials.splitlines():
        row = line.split(' ')
        if len(row) >= 1:
            try:
                unit=Unit.objects.get(serial_number=row[0])
            except:
                print('unit with serial number {} not found'.format(row[0]))
                continue
                # Need to find all of the LATEST light soak 10's
            result = unit.procedureresult_set.filter(disposition__name__iexact="in progress").first()
            print(result)
            result.disposition = None
            result.start_datetime = None
            result.end_datetime = None
            result.work_in_progress_must_comply = False
            result.save()
            for step in result.stepresult_set.filter(disposition__isnull=False):
                step.disposition = None
                step.start_datetime = None
                step.save()
                for measurement in step.measurementresult_set.filter(disposition__isnull=False):
                    measurement.result_double = None
                    measurement.result_datetime = None
                    measurement.date_time = None
                    measurement.user = None
                    measurement.disposition=None
                    measurement.save()

[
{
"execution_group_name": "Pre Stress",
"execution_group_number": 1,
"allow_skip": false,
"procedure_definition": 21
},
{
"execution_group_name": "Hail Strike #1",
"execution_group_number": 2,
"allow_skip": false,
"procedure_definition": 57
},
{
"execution_group_name": "Post Hail Strike #1",
"execution_group_number": 3,
"allow_skip": false,
"procedure_definition": 21
}
]

[
{
"execution_group_name": "Pre Stress",
"execution_group_number": 1,
"allow_skip": false,
"procedure_definition": 12
},
{
"execution_group_name": "Post Hail Strike #1",
"execution_group_number": 3,
"allow_skip": false,
"procedure_definition": 12
}
]


@transaction.atomic
def record_completion(procedure_result, start_datetime=None, end_datetime=None, username=None):
    """
    This action will mark a `procedure_result` as "Perfromed - Record only"
    Accepts a sparse POST of:
    {
        "procedure_result":$ID, // Required
        "start_datetime":YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ], // Optional, default Now()
        "end_datetime":YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ], // Optional, default Now()
        "user":username // Optional, default 'sysadmin'
    This is NON-Destructive. Dates and user will not overwrite existing data.
    }
    """
    errors=[]
    try:
        record = Disposition.objects.get(name__iexact='performed - record only')
    except:
        errors.append(
            "Error: required disposition configured incorrectly. Call Engineering!"
        )
        return Response(errors)
    try:
        result = ProcedureResult.objects.get(id=procedure_result)
    except:
        errors.append(
                "Error: requested procedure result {} does not exist".format(procedure_result)
            )
        return Response(errors)
    if not result.disposition == None:
        # This has a disposition, we don't want to change that
        errors.append(
                "Error: requested procedure result {} has a disposition of {}, cowardly not writing".format(result.id,result.disposition.name)
            )
        return Response(errors)
    # Should be working on a good POST body
    now_datetime = now()
    result.disposition = record
    if username:
        try:
            user = User.objects.get(username__iexact=username)
        except:
            errors.append(
                    "Error: requested user {} does not exist".format(username)
                )
            return Response(errors)
    else:
        user = User.objects.get(username__iexact='sysadmin')
    if start_datetime and result.start_datetime == None:
        result.start_datetime = start_datetime
    elif result.start_datetime == None:
        result.start_datetime = now_datetime
    if end_datetime and result.end_datetime == None:
        result.end = end_datetime
    elif result.end_datetime == None:
        result.end_datetime = now_datetime
    # Now push that data down to all non-skipable everything.
    # TODO: Speed this up by using bulk_update() -- MD
    for step in result.stepresult_set.filter(allow_skip=False):
        step.disposition = record
        # step.start_datetime = params.get('start_datetime',now_datetime)
        step.start_datetime = now_datetime
        for measurement in step.measurementresult_set.filter(allow_skip=False):
            measurement.disposition = record
            measurement.date_time = now_datetime
            measurement.user = user
            measurement.start_datetime = now_datetime
            measurement.save()
        step.save()
    result.save()

@transaction.atomic
def renumber_legs(serial):
    try:
        unit=Unit.objects.get(serial_number=serial)
    except:
        print('unit with serial number {} not found'.format(serial))
        return
    results = unit.procedureresult_set.all().order_by('linear_execution_group')
    for result in results:
        if result.linear_execution_group > 5:
            result.linear_execution_group -= 2
            print('setting to leg {}'.format(result.linear_execution_group))
            result.save()

@transaction atomic
def bulk_soak(serials):
    rows=[]
    for line in serials.splitlines():
        row = line.split(' ')
        if len(row) >= 1:
            try:
                unit=Unit.objects.get(serial_number=row[0])
            except:
                print('unit with serial number {} not found'.format(row[0]))
                continue
                # Need to find all of the LATEST light soak 10's
            results = unit.procedureresult_set.filter(name__icontains='light soak >10').order_by('name')
            last_run = int(results.last().name.split('#')[1])
            first_run = int(results.first().name.split('#')[1])
            offset = last_run * 2
            last_eg = results.last().linear_execution_group
            print('EG:',results.last().linear_execution_group)
            # get all of the procedures with EG > than this_run
            to_increment = unit.procedureresult_set.filter(linear_execution_group__gt = last_eg)
            for result in to_increment:
                # print('before:',result.linear_execution_group)
                result.linear_execution_group += 2
                # print('after:',result.linear_execution_group)
            ProcedureResult.objects.bulk_update(to_increment, ['linear_execution_group'])
            results = results.filter(name__endswith=first_run)
            this_run = int(last_run) +1
            for result in results:
                # last_eg += 1
                test_sequence = TestSequenceDefinition.objects.get(id=result.test_sequence_definition.id)
                procedures = test_sequence.procedureexecutionorder_set.filter(
                    execution_group_number = result.linear_execution_group,
                    procedure_definition = result.procedure_definition
                )
                if procedures.count() != 1:
                    print(
                            "Error: requested procedure test definition {} incorrect.".format(test_sequence.id),
                            " {} procedures returned, should only ever be 1".format(procedures.count())
                        )
                    break
                # Start constructing the new procedure_result:
                execution = procedures.all()[0]
                procedure_result = ProcedureResult.objects.create(
                    unit = result.unit,
                    name = '{}#{}'.format(execution.execution_group_name.split('#')[0],this_run),
                    disposition = None,
                    group = execution.procedure_definition.group,
                    work_order = result.work_order,
                    procedure_definition = execution.procedure_definition,
                    version = execution.procedure_definition.version,
                    linear_execution_group = execution.execution_group_number + offset,
                    test_sequence_definition = test_sequence,
                    allow_skip = execution.allow_skip,
                )
                for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
                    step_result = StepResult.objects.create(
                        name = step_execution.execution_group_name,
                        procedure_result = procedure_result,
                        step_definition = step_execution.step_definition,
                        execution_number = 0,
                        disposition = None,
                        start_datetime = None,
                        duration = 0,
                        test_step_result = None,
                        archived = False,
                        description = None,
                        step_number = 0,
                        step_type = step_execution.step_definition.step_type,
                        linear_execution_group = step_execution.execution_group_number,
                        allow_skip = step_execution.allow_skip,
                    )
                    for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                        measurement_result = MeasurementResult.objects.create(
                            step_result = step_result,
                            measurement_definition = measurement_definition,
                            software_revision = 0.0,
                            disposition = None,
                            limit = measurement_definition.limit,
                            station = 0,
                            name = measurement_definition.name,
                            record_only = measurement_definition.record_only,
                            allow_skip = measurement_definition.allow_skip,
                            requires_review = measurement_definition.requires_review,
                            measurement_type = measurement_definition.measurement_type,
                            order = measurement_definition.order,
                            report_order = measurement_definition.report_order,
                            measurement_result_type = measurement_definition.measurement_result_type,
                        )

def flush_all_tokens():
    from lsdb.authentication import token_expire_handler, expires_in, token_refresh
    from rest_framework.authtoken.models import Token
    for token in Token.objects.all():
        token_refresh(token)

def bulk_review():
    from django.utils import timezone
    from django.contrib.auth.models import User
    disposition = Disposition.objects.get(name__iexact='completed')
    user = User.objects.get(id=6)
    results = ProcedureResult.objects.filter(disposition__id=13,
        stepresult__measurementresult__date_time__lt='2021-03-08 00:00Z').distinct()
    for result in results:
        print(result.id)
        result.disposition = disposition
        result.save()
        for stepresult in result.stepresult_set.filter(disposition__isnull=False):
            stepresult.disposition = disposition
            stepresult.save()
            # print(stepresult.id)
            for measurement in stepresult.measurementresult_set.filter(disposition__isnull=False):
                measurement.reviewed_by_user = user
                measurement.review_datetime = timezone.now()
                measurement.disposition = disposition
                measurement.save()
                # print(measurement.id)
        # break

from django.db.models import Count
from django.db.models.functions import Trunc
results = ProcedureResult.objects.filter(disposition__isnull=False,
            stepresult__arcohived=False,
            stepresult__disposition__isnull=False,
            stepresult__measurementresult__date_time__gte='2021-02-28',
            stepresult__measurementresult__date_time__lte='2021-03-13',
            ).annotate(procedure=Count('procedure_definition',
            # distinct=True
            )).annotate(workday=Trunc('stepresult__measurementresult__date_time', 'day')
            ).values('workday','procedure','procedure_definition').order_by('workday')


from django.db import IntegrityError, transaction
@transaction.atomic
def position_swap(this):
    rows=[]
    for line in this.splitlines():
        row = line.split(' ')
        if len(row) >= 2:
            try:
                result_from=ProcedureResult.objects.get(id=row[0])
            except:
                print('source result with id {} not found'.format(row[0]))
                continue
            try:
                result_to=ProcedureResult.objects.get(id=row[1])
            except:
                print('source result with id {} not found'.format(row[1]))
                continue
            name_hold = result_to.name
            leg_hold = result_to.linear_execution_group
            result_to.name = result_from.name
            result_to.linear_execution_group = result_from.linear_execution_group
            result_to.save()
            result_from.name = name_hold
            result_from.linear_execution_group = leg_hold
            result_from.save()

position_swap('''49542 114922
49845 114925
49538 114918
49537 114917
''')
# asset test data:
#
# build_assets('''PVEL001,BKL,1
# PVEL002,BKL,1
# PVEL003,BKL,1
# PVEL004,BKL,1
# PVEL005,BKL,1
# PVEL006,BKL,1
# PVEL007,BKL,1
# PVEL008,BKL,1
# PVEL009,BKL,1
# PVEL059,BKL,1
# PVEL060,BKL,1
# PVEL145,SSF,1
# PVEL146,SSF,1
# PVEL147,SSF,1
# PVEL148,SSF,1
# GM1,DAV,7
# GM2,DAV,7
# GM3,DAV,7
# GM4,DAV,7
# GM5,DAV,7
# GM6,DAV,7
# GM7,DAV,7
# GM8,DAV,7
# GM9,DAV,7
# RT1,DAV,7
# RT2,DAV,7
# RT3,DAV,7
# RT4,DAV,7
# RT5,DAV,7
# RT6,DAV,7
# RT7,DAV,7
# RT8,DAV,7
# PLID East,DAV,7
# CRT1,DAV,7
# CRT2,DAV,7
# ''')
# '''
# HALM cetisPV,BKL,
# Eurotech Mechanical Load Tester,BKL,
# IIAM Test Station,SSF
# OIAM Test Station,DAV
# '''
# SerialNumber LEG
@transaction.atomic
def insert_marker(this):
    row=[]
    user = User.objects.get(id=6) # sysadmin
    completed = Disposition.objects.get(name__iexact='completed')
    marker = ProcedureDefinition.objects.get(name__iexact='marker')
    for line in this.splitlines():
        row = line.split(' ')
        try:
            unit = Unit.objects.get(serial_number=row[0])
            print(unit.id, unit.serial_number)
        except:
            print('serial number not found:', row[0])
            continue
        leg = unit.procedureresult_set.filter(linear_execution_group=row[1]).distinct().first()
        print(leg)
        if leg:
            # try:
            procedure_result = ProcedureResult.objects.create(
                unit = unit,
                name = leg.name,
                disposition = completed,
                group = marker.group,
                work_order = leg.work_order,
                procedure_definition = marker,
                version = marker.version,
                linear_execution_group = leg.linear_execution_group,
                test_sequence_definition = leg.test_sequence_definition,
                allow_skip = True,
                start_datetime = now(),
                end_datetime = now(),
            )
            # except:
            #     print('failed to create marker')
            #     continue
        else:
            print('execution group not found:', row[1])
            continue


from django.db import IntegrityError, transaction
from lsdb.models import Asset, AssetType, Disposition, Location
@transaction.atomic
def build_assets(this):
    row=[]
    disp = Disposition.objects.get(name__iexact='available')
    for line in this.splitlines():
        row = line.split(',')
        location = Location.objects.get(name=row[1])
        asset_type = AssetType.objects.get(id=row[2])
        asset = Asset.objects.create(
            name = '{} {}'.format(row[1], row[0]),
            disposition = disp,
            location = location,
        )
        asset.asset_types.add(asset_type)

#1.2 deployment migration:
@transaction.atomic
def initialize_tib():
    work_orders = WorkOrder.objects.all()
    for work_order in work_orders:
        if work_order.units.all():
            for unit in work_order.units.all():
                unit.tib = work_order.tib
                unit.save()

# Stress synthesis:
#serial, process, asset, LEG, start
#serial, process, asset, LEG, end


#serial, process, asset, LEG, start
@transaction.atomic
def start_chamber(this):
    row=[]
    user = User.objects.get(id=6) # sysadmin
    in_progress = Disposition.objects.get(name__iexact='in progress')
    completed = Disposition.objects.get(name__iexact='completed')
    for line in this.splitlines():
        row = line.split(',')
        try:
            unit = Unit.objects.get(serial_number=row[0])
            print(unit.id, unit.serial_number)
        except:
            print('serial number not found:', row[0])
            continue
        try:
            asset = Asset.objects.get(name = row[2])
        except:
            print('Asset not found:', row[2])
            continue
        try:
            result = unit.procedureresult_set.get(name = row[3], procedure_definition__name = row[1])
        except:
            print('Result Record not found, Procedure:', row[3], 'LEG',row[1])
            continue
        try:
            step = result.stepresult_set.get(name__iexact='test start')
        except:
            print('procedure missing test start step')
            continue
        try:
            measurement = step.measurementresult_set.get(name__iexact='start time')
        except:
            print('step missing test start measurement')
            continue
        try:
            write_procedure(result, in_progress,start_datetime=row[4])
        except:
            print('failure writing procedure:',result.id)
            continue
        try:
            write_step(step,completed,start_datetime=row[4])
        except:
            print('failure writing step:',step.id)
            continue
        try:
            write_measurement(measurement, completed, asset, user, 'result_datetime',row[4] )
        except:
            print('failure writing measurement:',measurement.id)
            continue

#serial, LEG, asset, process, start, end
@transaction.atomic
def complete_chamber(this):
    row=[]
    user = User.objects.get(id=6) # sysadmin
    completed = Disposition.objects.get(name__iexact='completed')
    for line in this.splitlines():
        row = line.split(',')
        try:
            unit = Unit.objects.get(serial_number=row[0])
            print(unit.id, unit.serial_number)
        except:
            print('serial number not found:', row[0])
            continue
        try:
            asset = Asset.objects.get(name = row[2])
        except:
            print('Asset not found:', row[2])
            continue
        try:
            result = unit.procedureresult_set.get(name = row[1], procedure_definition__name = row[3])
        except:
            print('Result Record not found, Procedure:', row[3], 'LEG',row[1])
            continue
        try:
            start_step = result.stepresult_set.get(name__iexact='test start')
        except:
            print('procedure missing test start step')
            continue
        try:
            end_step = result.stepresult_set.get(name__iexact='test end')
        except:
            print('procedure missing test end step')
            continue
        try:
            start_measurement = start_step.measurementresult_set.get(name__iexact='start time')
        except:
            print('step missing test start measurement')
            continue
        try:
            end_measurement = end_step.measurementresult_set.get(name__iexact='end time')
        except:
            print('step missing test start measurement')
            continue
        # try:
        write_procedure(result, completed,start_datetime=row[4],end_datetime=row[5])
        # except:
        #     print('failure writing procedure:',result.id)
        #     continue
        try:
            write_step(start_step,completed,start_datetime=row[4])
        except:
            print('failure writing step:',step.id)
            continue
        try:
            write_step(end_step,completed,end_datetime=row[5])
        except:
            print('failure writing step:',step.id)
            continue
        try:
            write_measurement(start_measurement, completed, asset, user, 'result_datetime',row[4] )
        except:
            print('failure writing measurement:',measurement.id)
            continue
        try:
            write_measurement(end_measurement, completed, asset, user, 'result_datetime',row[5] )
        except:
            print('failure writing measurement:',measurement.id)
            continue



close_fs6("S181128611110,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190202621405,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190213640197,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190403661754,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190424650253,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190424650267,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190430651121,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190430660279,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
close_fs6("S190430651123,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)

close_fs6("S190224690543,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)

4/15/2021  10:00:00 PM
"S200826670901, 10, BKL PVEL002,8/19/2021  10:00:00 PM,8/20/2021  9:14:22 PM", user
#"serial, LEGNAME, asset, process, start, end", user_object
# close_fs6("S190228611688,Pre Stress,BKL PVEL002,I-V Curve at STC (FS S6A),7/26/2021  10:00:00 PM, 7/27/2021  6:00:00 AM",user)
@transaction.atomic
def close_fs6(this, user=None):
    row=[]
    if not user:
        user = User.objects.get(id=6) # sysadmin
    reviewer = User.objects.get(id=6) # sysadmin
    completed = Disposition.objects.get(name__iexact='pass')
    for line in this.splitlines():
        row = line.split(',')
        try:
            unit = Unit.objects.get(serial_number=row[0])
            print(unit.id, unit.serial_number)
        except:
            print('serial number not found:', row[0])
            continue
        try:
            asset = Asset.objects.get(name = row[2])
        except:
            print('Asset not found:', row[2])
            continue
        try:
            result = unit.procedureresult_set.get(name = row[1], procedure_definition__name = row[3])
        except Exception as e:
            print(e)
            print('Result Record not found, Procedure:', row[3], 'LEG',row[1])
            continue
        try:
            start_step = result.stepresult_set.get(name__iexact='test start')
        except:
            print('procedure missing test start step')
            continue
        try:
            end_step = result.stepresult_set.get(name__iexact='test end')
        except:
            print('procedure missing test end step')
            continue
        try:
            start_measurement = start_step.measurementresult_set.get(name__iexact='start time')
        except:
            print('step missing test start measurement')
            continue
        try:
            end_measurement = end_step.measurementresult_set.get(name__iexact='end time')
        except Exception as e:
            print('step missing test end measurement:',e)
            continue
        try:
            write_procedure(result, completed,start_datetime=row[4],end_datetime=row[5],reviewer=reviewer)
        except Exception as e:
            print('failure writing procedure:',result.id, e)
            continue
        # try:
        #     write_step(start_step,completed,start_datetime=row[4])
        # except:
        #     print('failure writing step:',step.id)
        #     continue
        try:
            write_step(end_step,completed,end_datetime=row[5])
        except Exception as e:
            print('failure writing step:',end_step.id,e)
            continue
        # try:
        #     write_measurement(start_measurement, completed, asset, user, 'result_datetime',row[4] )
        # except:
        #     print('failure writing measurement:',measurement.id)
        #     continue
        try:
            write_measurement(end_measurement, completed, asset, user, 'result_datetime',row[5] )
        except:
            print('failure writing measurement:',measurement.id)
            continue

def fuck_time(string):
    import pytz
    from datetime import datetime
    from time import mktime
    from django.utils.timezone import make_aware
    naive_datetime = strptime(string.strip(), '%m/%d/%Y %I:%M:%S %p')
    dt = datetime.fromtimestamp(mktime(naive_datetime))
    aware = make_aware(dt, timezone=pytz.timezone('US/Pacific'))
    return str(aware)

def write_procedure(obj, disposition, start_datetime=None, end_datetime=None, reviewer=None):
    if start_datetime and obj.start_datetime == None: # Don't overwrite existing data...
        obj.start_datetime = fuck_time(start_datetime)
    if end_datetime and obj.end_datetime == None: # Don't overwrite existing data...:
        obj.end_datetime =fuck_time(end_datetime)
    obj.disposition = disposition
    obj.save()
    return

def write_step(obj, disposition, start_datetime=None, end_datetime=None):
    if start_datetime and obj.start_datetime == None:
        obj.start_datetime = fuck_time(start_datetime)
    if end_datetime and obj.end_datetime == None:
        obj.end_datetime =fuck_time(end_datetime)
    obj.disposition = disposition
    obj.save()
    return

def write_measurement(obj, disposition, asset, user, field_type, measurement, reviewer=None):
    obj.user = user
    obj.date_time = now()
    obj.asset = asset
    obj.result_datetime = fuck_time(measurement)
    obj.disposition = disposition
    if reviewer and obj.reviewed_by_user == None:
        obj.reviewed_by_user = reviewer
    obj.save()
    return
# verify_asset('A08201000300009','BKL EL')

def verify_asset(serial, asset):
    from lsdb.models import Asset, AssetType
    unit = Unit.objects.get(serial_number=serial)
    # Unit Disposition needs to be respected:
    if unit.disposition.complete:
        return Response({'message':'This serial number not in an active disposition. Contact engineering.'}, status = HTTP_400_BAD_REQUEST)
    if asset:
        # convert name string into asset object "BKL Wet Leakage Station",
        asset = Asset.objects.get(name__iexact=asset)
        # Check to see if this unit has *any* business at this asset type:
        if (asset.asset_types.filter(id__in=AssetType.objects.filter(proceduredefinition__procedureresult__unit=unit))):
            # Check for virgin module:
            if unit.procedureresult_set.filter(disposition__isnull=False,supersede__isnull=True):
                # some work done at some point, not a virgin
                # unit.fixture_location = asset
                # unit.save()
                # TODO: return the procedure result tree that is next for this asset:
                procedure_results = unit.procedureresult_set.filter(Q(disposition__isnull=True)|Q(disposition__complete=False))
                procedure_results = procedure_results.exclude(supersede=True)
                procedure_results = procedure_results.filter(procedure_definition__asset_types__in=asset.asset_types.all())
                procedure_results = procedure_results.order_by('linear_execution_group')
                # if definition:
                #     procedure_results = procedure_results.filter(procedure_definition__id=definition)
                procedure_results = procedure_results.annotate(done_to= Max('unit__procedureresult__linear_execution_group',
                    filter=Q(unit__procedureresult__disposition__isnull=False, unit__procedureresult__supersede__isnull=True)))
                for result in procedure_results:
                    print('Done to:', result.done_to)
                    if (result.done_to > result.linear_execution_group ) or (result.done_to < result.linear_execution_group -1):
                        procedure_results = procedure_results.exclude(id=result.id)
            else:
                # virgin module, send only first matching procedure:
                procedure_results = unit.procedureresult_set.filter(procedure_definition__asset_types__in=asset.asset_types.all())
                procedure_results = procedure_results.order_by('linear_execution_group')
                first_leg = procedure_results.first().linear_execution_group
                procedure_results = procedure_results.filter(linear_execution_group=first_leg)
            print('ProcedureResults',procedure_results)
            # TODO: Change such that step order execution is preserved.
            # serializer = ProcedureResultSerializer(procedure_results, many=True, context=self.context)
            # return Response(serializer.data)
        # TODO: Need a better return behavior here: return empty set for now
        print('Empty Set')

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# Modules in need of untwisting:
LRR904039200800500028 35
old_result: Pre Stress 8 Wet Leakage Current Test new_result: Pre Stress 8 Wet Leakage Current Test
old_result: Pre Stress 8 EL Image at 1.0x Isc new_result: Pre Light Soak 1 EL Image at 1.0x Isc
old_result: Pre Stress 8 EL Image at 0.1x Isc new_result: Pre Stress 8 EL Image at 0.1x Isc
old_result: Pre Stress 8 Visual Inspection new_result: Pre Stress 8 Visual Inspection

LRR904039200800500033 35
old_result: Pre Stress 8 Wet Leakage Current Test new_result: Pre Stress 8 Wet Leakage Current Test
old_result: Pre Stress 8 EL Image at 1.0x Isc new_result: Pre Light Soak 1 EL Image at 1.0x Isc
old_result: Pre Stress 8 EL Image at 0.1x Isc new_result: Pre Stress 8 EL Image at 0.1x Isc
old_result: Pre Stress 8 Visual Inspection new_result: Pre Stress 8 Visual Inspection

LRR904039200800600004 35
-old_result: Pre Stress 8 Wet Leakage Current Test new_result: Pre Stress 8 Wet Leakage Current Test
-old_result: Pre Stress 8 EL Image at 1.0x Isc new_result: Pre Light Soak 1 EL Image at 1.0x Isc
-old_result: Post SML 3 10 Wet Leakage Current Test new_result: Post SML 3 10 Wet Leakage Current Test
-old_result: Post SML 3 10 EL Image at 1.0x Isc new_result: Post Light Soak >30 kWh/m² 3 EL Image at 1.0x Isc
-old_result: Post DML 1000 12 Visual Inspection new_result: Pre Stress 8 Visual Inspection
-old_result: Post DML 1000 12 Wet Leakage Current Test new_result: Post DML 1000 12 Wet Leakage Current Test
-old_result: Post DML 1000 12 EL Image at 1.0x Isc new_result: Post Light Soak >10 kWh/m² #1 5 EL Image at 1.0x Isc
-old_result: Post TC 50 14 EL Image at 1.0x Isc new_result: Pre Stress 8 EL Image at 1.0x Isc
-old_result: Post TC 50 14 Wet Leakage Current Test new_result: Post TC 50 14 Wet Leakage Current Test
-old_result: Post TC 50 14 Visual Inspection new_result: Post SML 3 10 Visual Inspection
-old_result: Post HF 10 16 I-V Curve at LIC (Front) new_result: Pre Stress 8 I-V Curve at LIC (Front)
-old_result: Post HF 10 16 EL Image at 1.0x Isc new_result: Post SML 3 10 EL Image at 1.0x Isc
-old_result: Post HF 10 16 Wet Leakage Current Test new_result: Post HF 10 #1 16 Wet Leakage Current Test
-old_result: Post HF 10 16 Diode Test new_result: Post HF 10 #1 16 Diode Test
-old_result: Post HF 10 16 I-V Curve at STC (Front) new_result: Pre Light Soak 1 I-V Curve at STC (Front)
-old_result: Post HF 10 16 I-V Curve at STC (Rear) new_result: Pre Light Soak 1 I-V Curve at STC (Rear)
-old_result: Post HF 10 16 Visual Inspection new_result: Post DML 1000 12 Visual Inspection

LRR904039200800600014 35
old_result: Pre Stress 8 EL Image at 1.0x Isc new_result: Pre Light Soak 1 EL Image at 1.0x Isc
# old_result: Pre Stress 8 Wet Leakage Current Test new_result: Pre Stress 8 Wet Leakage Current Test
# old_result: Post SML 3 10 EL Image at 1.0x Isc new_result: Post Light Soak >30 kWh/m² 3 EL Image at 1.0x Isc
# old_result: Post SML 3 10 Wet Leakage Current Test new_result: Post SML 3 10 Wet Leakage Current Test
# old_result: Post DML 1000 12 EL Image at 1.0x Isc new_result: Post Light Soak >10 kWh/m² #1 5 EL Image at 1.0x Isc
# old_result: Post DML 1000 12 Visual Inspection new_result: Pre Stress 8 Visual Inspection
# old_result: Post DML 1000 12 Wet Leakage Current Test new_result: Post DML 1000 12 Wet Leakage Current Test
# old_result: Post TC 50 14 Wet Leakage Current Test new_result: Post TC 50 14 Wet Leakage Current Test
# old_result: Post TC 50 14 Visual Inspection new_result: Post SML 3 10 Visual Inspection
# old_result: Post TC 50 14 EL Image at 1.0x Isc new_result: Pre Stress 8 EL Image at 1.0x Isc
# old_result: Post HF 10 16 I-V Curve at LIC (Front) new_result: Pre Stress 8 I-V Curve at LIC (Front)
# old_result: Post HF 10 16 EL Image at 1.0x Isc new_result: Post SML 3 10 EL Image at 1.0x Isc
# old_result: Post HF 10 16 Wet Leakage Current Test new_result: Post HF 10 #1 16 Wet Leakage Current Test
# old_result: Post HF 10 16 Diode Test new_result: Post HF 10 #1 16 Diode Test
# old_result: Post HF 10 16 I-V Curve at STC (Rear) new_result: Pre Light Soak 1 I-V Curve at STC (Rear)
# old_result: Post HF 10 16 I-V Curve at STC (Front) new_result: Pre Light Soak 1 I-V Curve at STC (Front)
# old_result: Post HF 10 16 Visual Inspection new_result: Post DML 1000 12 Visual Inspection

LRR904039200801100008 35
old_result: Post SML 3 10 EL Image at 1.0x Isc new_result: Pre Light Soak 1 EL Image at 1.0x Isc
old_result: Post SML 3 10 Wet Leakage Current Test new_result: Pre Stress 8 Wet Leakage Current Test
old_result: Post DML 1000 12 EL Image at 1.0x Isc new_result: Post Light Soak >30 kWh/m² 3 EL Image at 1.0x Isc
old_result: Post DML 1000 12 Wet Leakage Current Test new_result: Post SML 3 10 Wet Leakage Current Test
old_result: Post DML 1000 12 Visual Inspection new_result: Pre Stress 8 Visual Inspection

LRR904039200801100013 35

old_result: Post LeTID 162 #2 11 EL Image at 1.0x Isc new_result: Pre Light Soak 1 EL Image at 1.0x Isc
old_result: Post LeTID 162 #3 13 Visual Inspection new_result: Pre Stress 5 Visual Inspection
old_result: Post LeTID 162 #3 13 Wet Leakage Current Test new_result: Pre Stress 5 Wet Leakage Current Test
old_result: Post LeTID 162 #3 13 I-V Curve at STC (Front) new_result: Pre Light Soak 1 I-V Curve at STC (Front)
old_result: Post LeTID 162 #3 13 EL Image at 1.0x Isc new_result: Post Light Soak 3 EL Image at 1.0x Isc
old_result: Post LeTID 162 #3 13 I-V Curve at LIC (Front) new_result: Pre Stress 5 I-V Curve at LIC (Front)
old_result: Post LeTID 162 #3 13 EL Image at 0.1x Isc new_result: Pre Stress 5 EL Image at 0.1x Isc
>>> lid_assign('PSTHMG00369 8')
old_result: Pre Light Soak 1 EL Image at 1.0x Isc new_result: Pre Light Soak 1 EL Image at 1.0x Isc
old_result: Pre Light Soak 1 I-V Curve at STC (Front) new_result: Pre Light Soak 1 I-V Curve at STC (Front)
old_result: Post Light Soak 3 EL Image at 1.0x Isc new_result: Post Light Soak >30 kWh/m² 3 EL Image at 1.0x Isc
old_result: Pre Stress 5 I-V Curve at LIC (Front) new_result: Pre Stress 7 I-V Curve at LIC (Front)
old_result: Pre Stress 5 Wet Leakage Current Test new_result: Pre Stress 7 Wet Leakage Current Test
old_result: Pre Stress 5 Visual Inspection new_result: Pre Stress 7 Visual Inspection
old_result: Pre Stress 5 EL Image at 0.1x Isc new_result: Pre Stress 7 EL Image at 0.1x Isc


@transaction.atomic
def aggregates(this):
    row=[]
    for line in this.splitlines():
        row = line.split(',')
        procdef = ProcedureDefinition.objects.get(id=row[0])
        procdef.aggregate_duration = round(float(row[2]))
        procdef.project_weight = round(float(row[1]))
        procdef.save()


'''1,18,5
2,18,10
3,18,7
4,792,262800
5,18,12
6,0,10
7,1990,60000
8,750,180
9,1800,14400
10,500,180
11,396,360
12,18,5
13,322.38,3888
14,18,10
15,34,5760
16,102,17280
17,136,23040
18,18,10
19,191.04,5760
20,1000,360
21,18,10
22,1310,1440
23,327.5,10080
24,946.4,18720
25,94.64,1872
26,946.4,18720
27,946.4,18720
28,94.64,1872
29,94.64,1872
31,191.04,5760
32,191.04,5760
33,18,10
34,95.52,2880
35,396,360
36,18,10
37,18,5
38,18,10
39,655.2,27040
40,396,131400
41,18,10
42,191.04,5760
43,191.04,5760
44,2200,525600
45,497.5,15000
46,750,30240
47,500,60
48,18,10
49,100,60
'''
@transaction.atomic
def stress_queue():
    # TODO: Fix issue with this query. Back to back stresses will show the second as available
    # if the first is in_progress
    queryset = ProcedureResult.objects.filter(disposition__isnull=True,
        unit__disposition__complete=False,
        group__name__iexact='stressors')\
        .exclude(test_sequence_definition__group__name__iexact="control")\
        .exclude(work_in_progress_must_comply=True)\
        .annotate(last_action_date = Max('unit__procedureresult__stepresult__measurementresult__date_time'))\
        .annotate(done_to= Max('unit__procedureresult__linear_execution_group',
            filter=Q(unit__procedureresult__disposition__isnull=False))).distinct()
    master_data_frame = pd.DataFrame(list(queryset.values(
        'unit__serial_number',
        'test_sequence_definition__name',
        'done_to',
        'linear_execution_group',
        'procedure_definition__name',
        'work_order__project__number',
        'work_order__name',
        'name',
        'allow_skip',
        'last_action_date',
        )))
    master_data_frame.fillna(1)
    master_data_frame['last_action_days'] = (timezone.now() - master_data_frame.last_action_date).astype("timedelta64[D]")
    # This takes out all the stps except the LEG we're on and the next one. This
    # is a major KLUGE to make up for the lack of allow_skip support.
    filtered = master_data_frame[master_data_frame.linear_execution_group >= master_data_frame.done_to][master_data_frame.linear_execution_group <= master_data_frame.done_to +1]
    fcols = filtered[[
        'unit__serial_number',
        'test_sequence_definition__name',
        'linear_execution_group',
        'procedure_definition__name',
        'work_order__project__number',
        'work_order__name',
        'name',
        'allow_skip',
        'last_action_date',
        'last_action_days',
    ]]
    fcols.columns = ['serial_number',
        'test_sequence','linear_execution_group','procedure_definition','project_number',
        'work_order','characterization','allow_skip','last_action_date','last_action_days',
    ]
    grouped = fcols.groupby('procedure_definition')
    full ={}
    for name, group in grouped:
        full[name]=group.to_dict(orient='records')
    # serializer = self.serializer_class(queryset, many=False, context=self.context)
    # print(serializer.data)
    print(full)

# Project Merge:
@transaction.atomic
def merge_projects(source_id=None, destination_id=None):
    project = Project.objects.get(id=destination_id)
    obsolete = Project.objects.get(id=source_id)
    work_orders = project.workorder_set.all()
    for note in obsolete.notes.all():
        project.notes.add(note)
        obsolete.notes.remove(note)
    for unit in obsolete.units.all():
        project.units.add(unit)
        obsolete.units.remove(unit)
    for expected_unit in obsolete.expectedunittype_set.all():
        expected_unit.project=project
        expected_unit.save()
    for work_order in obsolete.workorder_set.all():
        try:
            work_order.project=project
            work_order.save()
        except IntegrityError:
            # if there is a work_order with the same name here...
            work_order.name = 'imported_{}'.format(work_order.name)
            # Looks like I thought about conolidating these instead of renaming
            # target = work_orders.filter(name=work_order.name)
            # units
            # test_sequence_definition
            work_order.project=project
            work_order.save()
    if project.sfdc_number == None:
        project.sfdc_number = obsolete.sfdc_number
    if project.start_date == None:
        project.start_date = obsolete.start_date
    if project.invoice_date == None:
        project.invoice_date = obsolete.invoice_date
    if project.proposal_price == None:
        project.proposal_price = obsolete.proposal_price
    project.save()
    obsolete.delete()

    for oid in PlexusImport.objects.filter(lsdb_id=params.get('id'), lsdb_model='project'):
        oid.lsdb_id = project.id
        oid.save()

# Kevin's by_size query:
import sys
from lsdb.models import Unit
from django.utils.timezone import make_aware, activate, now, get_current_timezone
save_stdout = sys.stdout
with open('./lsdb/by_size.csv','w') as f:
    sys.stdout = f
    units = Unit.objects.filter(disposition__complete=False, workorder__isnull=False, procedureresult__stepresult__measurementresult__disposition__isnull=False).distinct()
    for unit in units:
        try:
            print('"=""{}""","{}","{}","{}","{}",{},{},"{}",{},{}'.format(
                unit.serial_number,
                unit.workorder_set.first().project.customer.name,
                unit.workorder_set.first().project.number,
                unit.workorder_set.first().name,
                unit.procedureresult_set.filter(
                    disposition__isnull=False,
                    stepresult__measurementresult__date_time__isnull=False,
                    ).order_by('-stepresult__measurementresult__datetime').first().test_sequence_definition.name,
                unit.unit_type.module_property.module_width,
                unit.unit_type.module_property.module_height,
                unit.procedureresult_set.filter(
                    disposition__isnull=False,
                    stepresult__measurementresult__date_time__isnull=False,
                    ).distinct().order_by('-stepresult__measurementresult__date_time').first().name,
                unit.procedureresult_set.filter(
                    disposition__isnull=False,
                    stepresult__measurementresult__date_time__isnull=False,
                    ).distinct().order_by('-stepresult__measurementresult__date_time').first().linear_execution_group,            (now() - unit.procedureresult_set.filter(disposition__isnull=False,
                    stepresult__measurementresult__date_time__isnull=False).distinct().order_by('-stepresult__measurementresult__date_time').first().stepresult_set.filter(measurementresult__date_time__isnull=False,
                        ).first().measurementresult_set.filter(date_time__isnull=False).first().date_time).days)
                    )
        except Exception as e:
            print('ERROR',e, unit.id, unit.serial_number)
    sys.stdout = save_stdout


    results = unit.procedureresult_set.filter(
        disposition__isnull=False,
        stepresult__measurementresult__date_time__isnull=False,
        ).distinct().order_by('-stepresult__measurementresult__date_time')
        try:
            print(unit.serial_number,results.first().linear_execution_group)







# DEPRECATED
# def swrap(this):
#     rows=[]
#     for line in this.splitlines():
#         row = line.split(' ')
#         if len(row) >= 2:
#             id=Unit.objects.get(serial_number=row[0]).id
#             rows.append( '{'+'"unit":"{}", "test_sequence":"{}"'.format(id,row[1])+'}')
#     print('[{}]'.format(',\n'.join(rows)))
