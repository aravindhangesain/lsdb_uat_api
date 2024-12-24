from rest_framework import viewsets
from lsdb.models import Disposition_pichina
from lsdb.serializers import Disposition_pichinaSerializer
from rest_framework import permissions
from rest_framework.response import Response

class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'GET'

class ProjectDisposition_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['GET']
    serializer_class = Disposition_pichinaSerializer
    permission_classes = [ReadOnlyPermission]
    pagination_class = None

    def get_queryset(self):
        specific_ids = [1, 7, 11, 12, 14, 15, 16, 20, 22, 25]
        return Disposition_pichina.objects.filter(id__in=specific_ids)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True,context={'request': request})
        data = {'results': serializer.data}
        return Response(data)

