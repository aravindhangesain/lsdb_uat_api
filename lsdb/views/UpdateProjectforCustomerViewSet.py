from rest_framework import viewsets
from rest_framework.response import Response
from lsdb.models import LocationLog, Project, WorkOrder, Unit, TestSequenceDefinition
from lsdb.serializers import UpdateProjectforCustomerSerializer
from lsdb.permissions import ConfiguredPermission
from django.utils import timezone

class UpdateProjectforCustomerViewSet(viewsets.ModelViewSet):
    logging_methods = ['PUT']
    queryset = Project.objects.all()
    permission_classes = [ConfiguredPermission]
    serializer_class = UpdateProjectforCustomerSerializer
    lookup_field = 'number'
    
    def update(self, request, *args, **kwargs):
        project_number=self.kwargs.get(self.lookup_field)
        project=Project.objects.filter(number=project_number).first()
        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Update all fields except disposition
        for field in serializer.validated_data:
            if field != 'disposition':
                setattr(project, field, serializer.validated_data[field])
        # Save the instance
        project.save()

     
        if 'disposition' in serializer.validated_data:
            new_disposition = serializer.validated_data['disposition']
            if new_disposition != project.disposition:
                # Update disposition ID of the project
                project.disposition = new_disposition
                project.save()
                # Update disposition ID of work orders associated with the project
                work_orders = WorkOrder.objects.filter(project=project.id)
                for work_order in work_orders:
                    work_order.disposition = new_disposition
                    work_order.save()
                    # Update disposition ID of units associated with the work order
                    units = Unit.objects.filter(workorder=work_order)
                    for unit in units:
                        unit.disposition = new_disposition
                        unit.save()
                    # Update test sequence definition of units
                    test_sequence_defs = TestSequenceDefinition.objects.filter(
                        testsequenceexecutiondata__work_order=work_order
                    )
                    for test_sequence_def in test_sequence_defs:
                        if test_sequence_def.disposition_id not in [3, 8]:
                            test_sequence_def.disposition = new_disposition
                            test_sequence_def.save()
            
                    
        
        if 'location' in request.data:
            location_url = request.data.get('location')
            location_id = location_url.rstrip('/').split('/')[-1] 
            if not LocationLog.objects.filter(project_id=project.id,location_id=location_id,is_latest=True).exists():
                if LocationLog.objects.filter(project_id=project.id):
                    LocationLog.objects.filter(project_id=project.id).update(is_latest=False)
                    LocationLog.objects.create(location_id=location_id,project_id=project.id,datetime=timezone.now(),flag=2,is_latest=True,username=self.request.user.username)
                else:
                    LocationLog.objects.create(location_id=location_id,project_id=project.id,datetime=timezone.now(),flag=2,is_latest=True,username=self.request.user.username)

                
        
        return Response(serializer.data)