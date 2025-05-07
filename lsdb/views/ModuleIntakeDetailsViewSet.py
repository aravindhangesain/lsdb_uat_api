from rest_framework import viewsets
from lsdb.models import ModuleIntakeDetails,NewCrateIntake
from lsdb.serializers import ModuleIntakeDetailsSerializer
from rest_framework.response import Response
from rest_framework import status

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
    