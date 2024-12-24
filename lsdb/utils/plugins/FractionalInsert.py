'''
This plugin inserts a full TSD into a unit test plan at the supplied execution group.
It guesses the work order for the new procedure results by looking at the last
procedure in the supplied execution group.

Input: (Run with serialize ON)
{
    "serial_number":"STRING",
    "tsd_id":INT,
    "execution_group":INT
}
Output:
'SUCCESS' or 'Exceptions:'

Limitations:
- The incoming TSD should not have more than 10 execution groups
- The target execution group should not have any fractional groups

either of these cases will lead to undesired behavior.

'''

class FractionalInsert():
    from django.db import IntegrityError, transaction

    def __init__(self):
        pass

    def _test(self):
        pass

    def _run(self:object, serial_number:str, tsd_id:int, execution_group:int):
        from lsdb.models import Unit, TestSequenceDefinition
        errors=[]
        try:
            unit=Unit.objects.get(serial_number=serial_number)
        except Exception as e:
            errors.append(
                    "Error: {} Serial: {}".format(e, serial_number)
            )
        try:
            tsd = TestSequenceDefinition.objects.get(id=tsd_id)
        except Exception as e:
            errors.append(
                    "Error: {} TSD_ID: {}".format(e, tsd_id)
            )
        try:
            # This guesses the work order by looking at the last one in the execution_group
            work_order = unit.procedureresult_set.filter(linear_execution_group=execution_group).last().work_order
            if not work_order:
                errors.append(
                    "Error: workorder not found for unit {}".format(serial_number)
                )
        except Exception as e:
            errors.append(
                    "Error: looking for workorder {}".format(e)
            )
        for execution in tsd.procedureexecutionorder_set.all():
            leg_num = float(execution.execution_group_number) * 0.1 + float(execution_group)
            leg_name = f'{execution.execution_group_name} (INSERTED)'
            try:
                #_build_procedure_bucket(unit, tsd, procedure_definition,work_order,leg_name, leg_num, allow_skip):
                self._build_procedure_bucket(unit,tsd,execution.procedure_definition,work_order,leg_name,leg_num,execution.allow_skip)
            except Exception as e:
                errors.append(
                    "Error: creating bucket {} Fatal".format(e)
                )
        if len(errors):
            response_dict = {"Exceptions":errors}
        else:
            response_dict = {"message":"SUCCESS"}
        return response_dict
        # response_dict = {'serial':serial_number, 'TSD':tsd_id, 'EG':execution_group}
        # return response_dict

    @transaction.atomic
    def _build_procedure_bucket(self, unit, tsd, procedure_definition,work_order,leg_name, leg_num, allow_skip):
        from lsdb.models import ProcedureResult, StepResult, MeasurementResult
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
