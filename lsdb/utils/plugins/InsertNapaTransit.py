class InsertNapaTransit():
    from django.db import IntegrityError, transaction
    """
    This plugin will use a predetermined TSD to insert procedure_results
    onto a unit's test plan. This will be the first opportunity to build in
    conditional execution intelligence. The magic is that we will add code into
    the execution_condition column of the TSD through table.
    for bifacial: "unit.unit_type.module_property.bifacial"
    for LIC: "unit.procedureresult_set.filter(procedure_definition__name__icontains='lic').count()>0"
    MAGIC
    To use this plugin:
    POST {
        "tsd":TSD_ID,
        "serials":["serial_1","serial_2", ... "serial_n"]
        }
    """
    def __init__(self:object):
        self.tsd = 114 #whatever it is

    def _test(self:object):
        return(None)

    def _run(self:object, serials:list=None, tsd:int=None):
        from lsdb.models import TestSequenceDefinition
        from lsdb.models import Unit
        from django.core.exceptions import ObjectDoesNotExist

        try:
            new_tsd = TestSequenceDefinition.objects.get(id=tsd)
        except ObjectDoesNotExist:
            return {'Error':'TSD ID {} does not exist'.format(self.tsd)}
        response_dict = {}
        for serial in serials:
            try:
                unit = Unit.objects.get(serial_number=serial)
            except ObjectDoesNotExist:
                response_dict[serial] = "Unit with serial {} does not exist".format(serial)
                continue
            try:
                work_order = unit.workorder_set.first()
            except:
                response_dict[serial] = "work order not found. please check serial".format(serial)
            try:
                done_to = unit.procedureresult_set.filter(
                        disposition__isnull=False,
                        test_sequence_definition__group__name__in=['Sequences','Control']
                    ).order_by('linear_execution_group').last().linear_execution_group
                response_dict[serial] =done_to
            except:
                response_dict[serial] = "something went wrong evaluating done_to. Are there any test results?"
            try:
                # self._build_bucket(work_order, new_tsd, done_to, unit)
                response_dict[serial]= self._build_bucket(work_order, new_tsd, done_to, unit)
            except:
                response_dict[serial] = "something went wrong building buckets: work_order:{} new_tsd:{} done_to:{} unit:{}".format(work_order, new_tsd, done_to, unit)

        return response_dict

    @transaction.atomic
    def _build_bucket(self:object, work_order:object, test_sequence:object, leg:float, unit:object):
        from lsdb.models import ProcedureResult
        from lsdb.models import StepResult
        from lsdb.models import MeasurementResult

        for execution in test_sequence.procedureexecutionorder_set.all():
            # Check if I should add this:
            if (not execution.execution_condition == None and len(execution.execution_condition)!=0):
                ldict = {'unit':unit,'retval':False}
                exec('retval={}'.format(execution.execution_condition),globals(),ldict)
                # we'll keep adding rear side flashes if we don't know
                if ldict['retval'] == False:
                    continue
            procedure_result = ProcedureResult.objects.create(
                unit = unit,
                name = execution.execution_group_name,
                disposition = None,
                group = execution.procedure_definition.group,
                work_order = work_order,
                procedure_definition = execution.procedure_definition,
                version = execution.procedure_definition.version,
                linear_execution_group = leg + execution.execution_group_number,
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
        return leg
