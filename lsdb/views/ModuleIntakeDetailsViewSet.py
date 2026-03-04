from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import ModuleIntakeDetailsSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

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
                    "tsd_name":procedure.test_sequence_definition.name if procedure else None,
                })

        return Response(response_data, status=status.HTTP_200_OK)