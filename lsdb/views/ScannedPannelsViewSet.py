from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from lsdb.models import ScannedPannels, ModuleIntakeDetails  # Import ModuleIntakeDetails model
from lsdb.serializers import ScannedPannelsSerializer

class ScannedPannelsViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ScannedPannels.objects.all()
    serializer_class = ScannedPannelsSerializer

    def create(self, request, *args, **kwargs):
        # Call the original create method to perform the creation
        response = super().create(request, *args, **kwargs)

        # Extract module intake id from request data
        module_intake = request.data.get("module_intake")
        
        if module_intake:
            # Find all items with the same module_intake
            related_items = ScannedPannels.objects.filter(module_intake=module_intake)
            # Serialize the related items
            serializer = self.get_serializer(related_items, many=True)
            # Modify the response structure as required
            response_data = [
                {
                    "module_intake": module_intake,
                    "items": [
                        {
                            "serial_number": item["serial_number"],
                            "test_sequence": item["test_sequence"],
                            "status": item["status"]
                        }
                        for item in serializer.data
                    ]
                }
            ]

            # Update the steps field to step 2 in ModuleIntakeDetails table
            ModuleIntakeDetails.objects.filter(id=module_intake).update(steps= 'step 2')

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return response
    