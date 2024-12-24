from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from django.db import connection
from lsdb.models import MeasurementResult, ScannedPannels, Unit, UnitType, WorkOrder, ModuleIntakeDetails, ProcedureResult, ProcedureExecutionOrder, StepResult, LocationLog
from lsdb.serializers import ScannedPannelsSerializer
from django.db import transaction
from django.utils import timezone

class BulkInsertforScannedpanelsViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ScannedPannels.objects.all()
    serializer_class = ScannedPannelsSerializer

    def create(self, request, *args, **kwargs):
        # Extract module intake id from request data
        module_intake_id = request.data.get("module_intake")
        items = request.data.get("scannedpanels", [])

        # Validate that items is a list
        if not isinstance(items, list):
            return Response({"error": "Items should be a list"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure module_intake is an object
        try:
            module_intake = ModuleIntakeDetails.objects.get(id=module_intake_id)
        except ModuleIntakeDetails.DoesNotExist:
            return Response({"error": "Invalid module_intake id"}, status=status.HTTP_400_BAD_REQUEST)

        # Create instances of ScannedPannels
        created_items = []
        for item in items:
            item_data = {
                "module_intake": module_intake_id,
                "serial_number": item["serial_number"],
                "test_sequence": item["test_sequence"],
                "status": item["status"]
            }
            serializer = self.get_serializer(data=item_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            created_items.append(serializer.instance)

        # Process created_items to create Unit instances and add entries to workorder_units
        for item in created_items:
            newcrateintake_id = module_intake.newcrateintake.id
            serial_number = item.serial_number
            location_id = module_intake.location.id
            unit_type_id = self.get_unit_type_id(item)

            if unit_type_id is not None:
                if not Unit.objects.filter(serial_number=serial_number, unit_type_id=unit_type_id).exists():
                    # Create Unit instance
                    new_unit = Unit.objects.create(
                        serial_number=serial_number,
                        location_id=location_id,
                        unit_type_id=unit_type_id
                    )

                    # Fetch BOM from the module_intake table using newcrateintake_id
                    bom_string = module_intake.bom  # Replace 'bom' with the actual field name for BOM in the module_intake table
                    if bom_string:
                        bom_items = bom_string.split(',')  # Split the BOM string into a list of workorder descriptions

                        # Prepare SQL for inserting into workorder_units
                        with connection.cursor() as cursor:
                            # Fetch the primary key of the workorder entry based on the workorder description and project_id
                            try:
                                workorder = WorkOrder.objects.get(name=module_intake.bom, project_id=module_intake.projects_id)
                                workorder_id = workorder.id
                            except WorkOrder.DoesNotExist:
                                continue  # Skip if the workorder is not found

                            # Insert into workorder_units
                            cursor.execute("""
                                INSERT INTO lsdb_workorder_units (workorder_id, unit_id)
                                VALUES (%s, %s)
                            """, [
                                workorder_id,  # Primary key of the workorder
                                new_unit.id    # ID of the newly created Unit
                            ])

                    # Insert into project_units
                    project_id = module_intake.projects_id  # Get project_id from module_intake
                    if project_id:
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO lsdb_project_units (unit_id, project_id)
                                VALUES (%s, %s)
                            """, [
                                new_unit.id,    # ID of the newly created Unit
                                project_id      # Project ID from module_intake
                            ])

                    # Insert records into ProcedureResult table
                    if item.test_sequence:
                        self.build_bucket(workorder, item.test_sequence, new_unit)

        # Only process LocationLog for serial_numbers provided in this POST request
        serial_numbers_from_request = [item["serial_number"] for item in items]

        # Fetch unit_ids for the current request's serial_numbers
        unit_ids = Unit.objects.filter(serial_number__in=serial_numbers_from_request).values_list('id', flat=True)

        # Create LocationLog entries for these unit_ids
        location_id = module_intake.location_id
        if location_id:
            for unit_id in unit_ids:
                LocationLog.objects.create(
                    location_id=location_id,
                    is_latest=True,
                    unit_id=unit_id,
                    flag=1,
                    datetime=timezone.now(),
                    username=self.request.user.username
                )

        # Create the response structure
        response_data = {
            "module_intake": module_intake_id,
            "scannedpanels": [
                {
                    "serial_number": item["serial_number"],
                    "test_sequence": item["test_sequence"],
                    "status": item["status"]
                }
                for item in items
            ]
        }

        # Update the steps field to step 2 in ModuleIntakeDetails table
        ModuleIntakeDetails.objects.filter(id=module_intake_id).update(steps='step 2')

        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    def build_bucket(self, work_order, test_sequence, unit):
        for execution in test_sequence.procedureexecutionorder_set.all():
            # Check if I should add this:
            if (not execution.execution_condition == None and len(execution.execution_condition)!=0):
                ldict = {'unit': unit, 'retval': False}
                exec('retval={}'.format(execution.execution_condition), None, ldict)
                # we'll keep adding rear side flashes if we don't know
                if ldict['retval'] == False:
                    continue
            # print(procedure.procedureexecutionorder_set.all()[0])
            procedure_result = ProcedureResult.objects.create(
                unit=unit,
                name=execution.execution_group_name,
                disposition=None,
                group=execution.procedure_definition.group,
                work_order=work_order,
                procedure_definition=execution.procedure_definition,
                version=execution.procedure_definition.version,
                linear_execution_group=execution.execution_group_number,
                test_sequence_definition=test_sequence,
                allow_skip=execution.allow_skip,
            )
            for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
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
                    measurement_result = MeasurementResult.objects.create(
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
    
    def get_unit_type_id(self, obj):
        try:
            module_type = obj.module_intake.module_type
            unit_type = UnitType.objects.get(model=module_type)
            return unit_type.id
        except UnitType.DoesNotExist:
            return None
