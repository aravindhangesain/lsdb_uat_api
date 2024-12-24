from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from lsdb.models import ExpectedUnitType, UnitType, WorkOrder
from lsdb.serializers import GetModelTypeSerializer

class GetModelTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows UnitType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = UnitType.objects.all()
    serializer_class = GetModelTypeSerializer
    lookup_field = 'name'  # Use BOM as the lookup field

    def retrieve(self, request, *args, **kwargs):
        name = kwargs.get('name', None)
        project_id = request.query_params.get('project_id', None)

        if name is not None and project_id is not None:
            # Check if WorkOrder exists with the given BOM name and project_id
            work_order_exists = WorkOrder.objects.filter(name=name, project_id=project_id).exists()

            if work_order_exists:
                # Get the unit_type IDs from the ExpectedUnitType records
                expected_unit_types = ExpectedUnitType.objects.filter(project_id=project_id).values('unit_type_id').distinct()

                if expected_unit_types.exists():
                    # Get the unit_type IDs from the ExpectedUnitType records
                    unit_type_ids = [item['unit_type_id'] for item in expected_unit_types]

                    # Retrieve the UnitType records for those IDs
                    matching_unit_types = UnitType.objects.filter(id__in=unit_type_ids).values('id', 'model')  # Include the fields you need

                    # Return the matching UnitType data
                    return Response(list(matching_unit_types), status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "No matching expected unit types found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"detail": "No matching work order found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "Name or project_id not provided."}, status=status.HTTP_400_BAD_REQUEST)
