from rest_framework import viewsets, status
from rest_framework.response import Response
from lsdb.models import Unit, ProcedureResult, StepResult, MeasurementResult
from lsdb.serializers import ProcedureUpdateSerializer

class ProcedureUpdateViewSet(viewsets.ViewSet):
    queryset = Unit.objects.none()  # Dummy queryset
    serializer_class = ProcedureUpdateSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                s = [71]
                serial_numbers = serializer.validated_data["serial_numbers"]
                success_serial_numbers = []
                error_serial_numbers = {}

                for serial_number in serial_numbers:
                    unit_id = Unit.objects.filter(serial_number=serial_number).values_list('id', flat=True).first()
                    if not unit_id:
                        error_serial_numbers[serial_number] = "Unit not found"
                        continue

                    procedure_results = ProcedureResult.objects.filter(unit_id=unit_id, procedure_definition_id__in=s)
                    for procedure_result in procedure_results:
                        existing_step_result = StepResult.objects.filter(
                            procedure_result=procedure_result,
                            step_definition_id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
                        ).exists()

                        if not existing_step_result:
                            for step_execution in procedure_result.procedure_definition.stepexecutionorder_set.filter(step_definition_id__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]):
                                step_result = StepResult.objects.create(
                                    name=step_execution.execution_group_name,
                                    procedure_result=procedure_result,
                                    step_definition=step_execution.step_definition,
                                    execution_number=0,
                                    disposition=None,
                                    start_datetime=None,
                                    duration=0,
                                    test_step_result=None,
                                    archived=False,
                                    description=None,
                                    step_number=0,
                                    step_type=step_execution.step_definition.step_type,
                                    linear_execution_group=step_execution.execution_group_number,
                                    allow_skip=step_execution.allow_skip,
                                )
                                for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                                    MeasurementResult.objects.create(
                                        step_result=step_result,
                                        measurement_definition=measurement_definition,
                                        software_revision=0.0,
                                        disposition=None,
                                        limit=measurement_definition.limit,
                                        station=0,
                                        name=measurement_definition.name,
                                        record_only=measurement_definition.record_only,
                                        allow_skip=measurement_definition.allow_skip,
                                        requires_review=measurement_definition.requires_review,
                                        measurement_type=measurement_definition.measurement_type,
                                        order=measurement_definition.order,
                                        report_order=measurement_definition.report_order,
                                        measurement_result_type=measurement_definition.measurement_result_type,
                                    )
                    success_serial_numbers.append(serial_number)
                return Response({
                    "success": f"Step results updated successfully for {len(success_serial_numbers)} serial numbers",
                    "failed": error_serial_numbers
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
