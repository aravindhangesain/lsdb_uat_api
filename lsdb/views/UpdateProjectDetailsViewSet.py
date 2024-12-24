from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.test import APIRequestFactory
from lsdb.models import Project
from lsdb.serializers import UpdateProjectDetailsSerializer, ProjectSerializer
from lsdb.permissions import ConfiguredPermission
from lsdb.views import ProjectModifiedDetailsViewSet

class UpdateProjectDetailsViewSet(viewsets.ModelViewSet):
    logging_methods = ['PUT']
    queryset = Project.objects.all()
    permission_classes = [ConfiguredPermission]
    lookup_field = 'number'

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UpdateProjectDetailsSerializer
        else:
            return ProjectSerializer
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Check if proposal_price is None, if yes, get the current value from the database
        if 'proposal_price' in serializer.validated_data and serializer.validated_data['proposal_price'] is None:
            current_proposal_price = Project.objects.get(pk=instance.pk).proposal_price
            serializer.validated_data['proposal_price'] = current_proposal_price

        if 'start_date' in serializer.validated_data and serializer.validated_data['start_date'] is None:
            current_start_date = Project.objects.get(pk=instance.pk).start_date
            serializer.validated_data['start_date'] = current_start_date

        comments = serializer.validated_data.pop('comments', None)

        self.perform_update(serializer)

        # Trigger the post request to ProjectModifiedDetails with the updated project number
        self.trigger_post_request(instance.number,comments)
        return Response(serializer.data)
    
    def trigger_post_request(self, number,comments):
        # Create a new instance of HttpRequest using APIRequestFactory
        factory = APIRequestFactory()
        data = {
            'number': number,
            'comments':comments,
            # Include other fields as needed
        }

        # Include authentication details in the triggered request
        request = factory.post('http://lsdbhaveblueuat.azurewebsites.net/api/1.0/projectmodifieddetails/', data=data)
        request.user = self.request.user

        # Include context data if needed
        view = ProjectModifiedDetailsViewSet.as_view({'post': 'create'})
        response = view(request)

        # Process the response if needed
        if response.status_code == 201:  # HTTP 201 Created
            print("ProjectModifiedDetails created successfully")
        else:
            print("Failed to create ProjectModifiedDetails")