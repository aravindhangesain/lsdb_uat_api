from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import ModuleIntakeDetailsSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Q
import requests
from datetime import datetime
from django.db import transaction
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from lsdb.views.BulkInsertforScannedpanelsViewSet import BulkInsertforScannedpanelsViewSet

class ModuleIntakeDetailsViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ModuleIntakeDetails.objects.all().order_by('-intake_date')
    serializer_class = ModuleIntakeDetailsSerializer
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        module_intake_details = serializer.save(steps='step 1')

        project_id = module_intake_details.projects_id

        if project_id:
            try:
                new_crate_intake = NewCrateIntake.objects.get(id=module_intake_details.newcrateintake_id)
                new_crate_intake.project_id = project_id
                new_crate_intake.save()
            except NewCrateIntake.DoesNotExist:
                pass
            
        return module_intake_details
    
    @action(detail=False, methods=['get'])
    def project_details(self, request):
        project_id = request.query_params.get('project_id')

        if not project_id:
            return Response(
                {"error": "Project ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        intake_details = ModuleIntakeDetails.objects.filter(
            projects_id=project_id
        ).select_related("projects")
        
        if not intake_details.exists():
            return Response(
                {"error": "No intake details found for the given project ID."},
                status=status.HTTP_404_NOT_FOUND
            )

        response_data = []

        for intake in intake_details:

            project_units = intake.projects.units.all()

            for unit in project_units:
                procedure = ProcedureResult.objects.filter(
                    unit_id=unit.id
                ).first()

                workorder = WorkOrder.objects.filter(
                    project_id=project_id,
                    units=unit
                ).first()

                response_data.append({
                    "serial_number": unit.serial_number,
                    "work_order_name": workorder.name if workorder else None,
                    "intake_id": intake.id,
                    "tsd_name":procedure.test_sequence_definition.name if procedure else None

                })

        return Response(response_data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=False, methods=['post','get'])
    def migrate_sns(self,request):

        if request.method =='POST':

            serial_numbers=request.data.get('serial_numbers')
            project_id=request.data.get('project_id')
            workorder_id=request.data.get('workorder_id')

            is_newworkorder=request.data.get('is_newworkorder')

            project=Project.objects.get(id=project_id)
            workorder=WorkOrder.objects.get(id=workorder_id)

            if is_newworkorder==1:

                scannedpanels=[]

                for serial_number in serial_numbers:

                    unit=Unit.objects.get(serial_number=serial_number)

                    # capture initial state
                    initial_project = Project.objects.filter(units=unit).first()
                    initial_workorder = WorkOrder.objects.filter(units=unit).first()
                    initial_serial_number = unit.serial_number

                    # remove old project and workorder links
                    Project.units.through.objects.filter(unit_id=unit.id).delete()
                    WorkOrder.units.through.objects.filter(unit_id=unit.id).delete()

                    scannedpanels.append({
                        "serial_number":serial_number,
                        "module_type":unit.unit_type.model,
                        "test_sequence":"",
                        "status":True
                    })

                    # save migration history
                    UnitMigrationHistory.objects.create(
                        initial_serial_number=initial_serial_number,
                        initial_project=initial_project,
                        initial_workorder=initial_workorder,
                        migrated_serial_number=serial_number,
                        migrated_project=project,
                        migrated_workorder=workorder,
                        migrated_by=request.user
                    )

                    project.units.add(unit.id)
                    workorder.units.add(unit.id)

                crate_intake = NewCrateIntake.objects.filter(project_id=project_id).first()

               

                module_intake = ModuleIntakeDetails.objects.create(
                    lot_id="SRI",
                    bom=workorder.name,
                    module_type=unit.unit_type.model,
                    number_of_modules=len(serial_numbers),
                    location_id=1,
                    projects_id=project.id,
                    customer_id=project.customer.id,
                    newcrateintake_id=crate_intake.id,
                    intake_date=datetime.now().isoformat(),
                    received_date=datetime.now().isoformat(),
                    steps=3
                )

                return Response({"message": "Migration completed"})

                
                
                


            elif is_newworkorder==0:

                scannedpanels=[]

                for serial_number in serial_numbers:

                    unit=Unit.objects.get(serial_number=serial_number)

                    # capture initial state
                    initial_project = Project.objects.filter(units=unit).first()
                    initial_workorder = WorkOrder.objects.filter(units=unit).first()
                    initial_serial_number = unit.serial_number

                    # new_unit = Unit.objects.create(
                    #     unit_type=unit.unit_type if unit.unit_type else None,
                    #     fixture_location=unit.fixture_location if unit.fixture_location else None,
                    #     serial_number=(unit.serial_number + "-1") if unit.serial_number else None,
                    #     location=unit.location if unit.location else None,
                    #     name=unit.name if unit.name else None,
                    #     description=unit.description if unit.description else None,
                    #     old_notes=unit.old_notes if unit.old_notes else None,
                    #     disposition=unit.disposition if unit.disposition else None,
                    #     tib=unit.tib if unit.tib else None,
                    #     intake_date=unit.intake_date if unit.intake_date else None
                    # )

                    scannedpanels.append({
                        "serial_number":unit.serial_number+str(-1),
                        "module_type":unit.unit_type.model,
                        "test_sequence":"",
                        "status":True
                    })

                    # save migration history
                    UnitMigrationHistory.objects.create(
                        initial_serial_number=initial_serial_number,
                        initial_project=initial_project,
                        initial_workorder=initial_workorder,
                        migrated_serial_number=unit.serial_number+str(-1),
                        migrated_project=project,
                        migrated_workorder=workorder,
                        migrated_by=request.user
                    )

                crate_intake = NewCrateIntake.objects.filter(project_id=project_id).first()

                module_intake = ModuleIntakeDetails.objects.create(
                    lot_id="SRI",
                    bom=workorder.name,
                    module_type=unit.unit_type.model,
                    number_of_modules=len(serial_numbers),
                    location_id=1,
                    projects_id=project.id,
                    customer_id=project.customer.id,
                    newcrateintake_id=crate_intake.id,
                    intake_date=datetime.now().isoformat(),
                    received_date=datetime.now().isoformat()
                )

                payload2={
                    "scannedpanels":scannedpanels,
                    "module_intake":module_intake.id
                }

                request._request.data = payload2

           

                view = BulkInsertforScannedpanelsViewSet()
                view.request = request
                view.action = "create"
                view.args = ()
                view.kwargs = {}
                view.format_kwarg = None

                response2 = view.create(request._request)

                if response2.status_code != 201:
                    return Response(
                    {"error": "Intake Failure2", "details": response2.data},
                    status=status.HTTP_400_BAD_REQUEST)

                return Response({"message": "Migration completed"})

        return Response({"message": "boilerplate get"})