from rest_framework import viewsets
from lsdb.permissions import ConfiguredPermission
from lsdb.models import ProjectModifiedDetails
from lsdb.serializers import ProjectModifiedDetailsSerializer
from rest_framework.response import Response


class ProjectModifiedDetailsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Project to be viewed or edited.
    """
    logging_methods = ['GET','POST','PUT','PATCH']
    # queryset = ProjectModifiedDetails.objects.all()
    serializer_class = ProjectModifiedDetailsSerializer
    permission_classes = [ConfiguredPermission]
    lookup_field = 'number'

    def perform_create(self, serializer):
        # Automatically set the 'modified_by' field to the currently logged-in user
        serializer.save(modified_by=self.request.user)

    def perform_update(self, serializer):
        # Automatically set the 'modified_by' field to the currently logged-in user
        serializer.save(modified_by=self.request.user)

    def get_queryset(self):
        return ProjectModifiedDetails.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        number = kwargs.get('number')
        queryset = self.get_queryset()
        project_details = queryset.filter(number=number)
        serializer = self.get_serializer(project_details, many=True)
        response_data = {'project_details': serializer.data}
        return Response(response_data)

