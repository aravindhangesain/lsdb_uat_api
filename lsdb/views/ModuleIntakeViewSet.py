from rest_framework import viewsets
from lsdb.models import ModuleIntake, Unit, Project, Customer, WorkOrder, NewCrateIntake,Location,LocationLog
from lsdb.serializers import ModuleIntakeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection
from django.db.models import Q

class ModuleIntakeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ModuleIntake to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ModuleIntake.objects.all()
    serializer_class = ModuleIntakeSerializer
    
    @action(detail=False, methods=['get'])
    def details(self, request):
        with connection.cursor() as cursor:
            query = """
                SELECT DISTINCT p.id, p.number, p.customer_id
                FROM lsdb_project p
            """
            cursor.execute(query)
            projects = cursor.fetchall()
        if not projects:
            return Response([])
        
        project_list = []
        for row in projects:
            project_id,project_number,customer_id = row

            try:
                customer = Customer.objects.get(id=customer_id)
                customer_data = {
                    'customer_id': customer.id,
                    'customer_name': customer.name,
                }

            except Customer.DoesNotExist:
                customer_data = {
                    'customer_id': None,
                    'customer_name': 'Unknown',
                }

            try:
                project = LocationLog.objects.get(project_id=project_id,is_latest=True,flag=2)
                location_id = project.location_id  

                if location_id: 
                    try:
                        location = Location.objects.get(id=location_id)
                        
                        location_data = {
                            'location_id': location_id,
                            'location_name': location.name  
                        }
                    except LocationLog.DoesNotExist:
                        location_data = {
                            'location_id': location_id,
                            'location_name': None
                        }
                else:
                    location_data = {
                        'location_id': None,
                        'location_name': None  
                    }
            except LocationLog.DoesNotExist:
                location_data = {
                    'location_id': None,
                    'location_name': None
                }

            workorder_names = WorkOrder.objects.filter(project_id=project_id).values_list('name', flat=True)

            crate_intake_ids = NewCrateIntake.objects.filter(
                Q(project_id=project_id) | (Q(project_id__isnull=True) & Q(customer_id=customer_id))
            ).values_list('id','crate_name')

            if not crate_intake_ids:
                pass

            project_data = {
                'project': {
                    'project_id': project_id,
                    'project_number': project_number,
                    },
                'customer': customer_data,
                'location_data':location_data,
                'bom': list(workorder_names),
                'crate_intake_ids': list(crate_intake_ids)  
            }

            project_list.append(project_data)
        return Response(project_list)
