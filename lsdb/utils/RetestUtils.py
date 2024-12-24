import json
from django.db import IntegrityError, transaction
from django.utils import timezone
# from rest_framework.response import Response

from lsdb.models import Disposition
from lsdb.models import MeasurementResult
from lsdb.models import ProcedureResult
from lsdb.models import StepResult

from lsdb.serializers.ProcedureResultSerializer import ProcedureResultSerializer

class RetestUtils():
    def __init__(self):
        pass

    @transaction.atomic
    def retest_procedure(self, request=None, pk=None):
        serializer_class = ProcedureResultSerializer
        """
        Accepts a sparse POST of:
        {
            "procedure_result":$ID
        }
        This action needs to mark the current step result archived=true
        """
        errors=[]
        self.context={'request':request}
        try:
            retest = Disposition.objects.get(name__iexact='retest required')
        except:
            errors.append(
                "Error: restest required disposition configured incorrectly. Call Engineering!"
            )
            return errors
        if request.method == "POST":
            params = json.loads(request.body)
            if pk:
                result = ProcedureResult.objects.get(id=pk)
            else:
                try:
                    result = ProcedureResult.objects.get(id=params.get('procedure_result'))
                except:
                    errors.append(
                            "Error: requested procedure result {} does not exist".format(params.get('procedure_result'))
                        )
                    return errors

            # Start constructing the new procedure_result:
            execution = result.procedure_definition
            procedure_result = ProcedureResult.objects.create(
                unit = result.unit,
                name = result.name,
                disposition = None,
                group = result.group,
                work_order = result.work_order,
                procedure_definition = execution,
                version = result.version,
                linear_execution_group = result.linear_execution_group,
                test_sequence_definition = result.test_sequence_definition,
                allow_skip = result.allow_skip,
            )
            for step_execution in execution.stepexecutionorder_set.all():
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
            # new record created, supersede the old one:
            result.supersede=True
            result.disposition = retest
            result.reviewed_by_user = request.user
            result.review_datetime = timezone.now()
            result.save()
            # This should only be changing those dispositions of "requires retest"
            for stepresult in result.stepresult_set.filter(disposition__isnull=False):
                stepresult.disposition = retest
                stepresult.save()
                for measurement in stepresult.measurementresult_set.filter(disposition__isnull=False):
                    measurement.reviewed_by_user = request.user
                    measurement.review_datetime = timezone.now()
                    measurement.disposition = retest
                    measurement.save()
            # TODO: Synch childern dispositions:
            # result.stepresult_set.all().update(disposition=retest)
            # result.update(stepresult_set____measurement_disposition
            serializer = ProcedureResultSerializer(procedure_result, many=False, context=self.context)
        else:
            serializer = ProcedureResultSerializer([], many=True, context=self.context)
        return serializer.data
