from rest_framework import viewsets
from lsdb.models import Disposition
from lsdb.serializers import DispositionSerializer
from rest_framework import permissions
from rest_framework.response import Response

class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow only GET method
        return request.method == 'GET'

class ProjectDispositionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Dispositions to be viewed or edited.
    """
    logging_methods = ['GET']
    serializer_class = DispositionSerializer
    permission_classes = [ReadOnlyPermission]
    pagination_class = None

    def get_queryset(self):

        # Filter queryset to include only specific IDs
        specific_ids = [1, 7, 11, 12, 14, 15, 16, 20, 22, 25]
        return Disposition.objects.filter(id__in=specific_ids)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {'results': serializer.data}
        return Response(data)

