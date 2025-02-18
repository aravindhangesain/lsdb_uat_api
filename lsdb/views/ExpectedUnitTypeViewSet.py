from rest_framework import viewsets
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import ExpectedUnitTypeSerializer
from lsdb.models import ExpectedUnitType
from lsdb.permissions import ConfiguredPermission
from rest_framework.decorators import action
from rest_framework.response import Response


class ExpectedUnitTypeViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows ExpectedUnitType to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ExpectedUnitType.objects.all()
    serializer_class = ExpectedUnitTypeSerializer
    permission_classes = [ConfiguredPermission]


    @action(detail=False, methods=['get'], url_path='by-project')
    def get_by_project(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({"detail": "project_id query parameter is required."}, status=400)

        filtered_queryset = self.queryset.filter(project_id=project_id)
        serializer = self.get_serializer(filtered_queryset, many=True)
        return Response(serializer.data)
