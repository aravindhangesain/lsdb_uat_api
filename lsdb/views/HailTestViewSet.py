from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import connection
from lsdb.models import HailTest, ProcedureResult, Unit, Project
from lsdb.serializers import HailTestSerializer
from rest_framework.reverse import reverse

class HailTestViewSet(viewsets.ModelViewSet):
    queryset = HailTest.objects.all()
    serializer_class = HailTestSerializer

    @action(detail=False, methods=['get'], url_path='by-serial/(?P<serial_number>[^/.]+)')
    def get_by_serial(self, request, serial_number=None):
        try:
            unit = Unit.objects.get(serial_number=serial_number)
        except Unit.DoesNotExist:
            return Response({"error": "Unit not found"}, status=status.HTTP_404_NOT_FOUND)
        hailtests = HailTest.objects.filter(unit=unit)
        if not hailtests.exists():
            return Response({"message": "No HailTest records found for this serial number"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(hailtests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='create-from-serial')
    def create_from_serial_number(self, request):
        serial_number = request.query_params.get('serial_number')
        if not serial_number:
            return Response({"error": "serial_number is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            unit = Unit.objects.get(serial_number=serial_number)
            unit_id = unit.id
        except Unit.DoesNotExist:
            return Response({"error": "Unit not found for given serial number"}, status=status.HTTP_404_NOT_FOUND)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT workorder_id 
                FROM lsdb_workorder_units 
                WHERE unit_id = %s 
                LIMIT 1
            """, [unit_id])
            workorder_row = cursor.fetchone()
        if not workorder_row:
            return Response({"error": "No workorder mapping found for this unit"}, status=status.HTTP_404_NOT_FOUND)
        workorder_id = workorder_row[0]
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT project_id 
                FROM lsdb_project_units 
                WHERE unit_id = %s 
                LIMIT 1
            """, [unit_id])
            project_row = cursor.fetchone()
        if not project_row:
            return Response({"error": "No project mapping found for this unit"}, status=status.HTTP_404_NOT_FOUND)
        project_id = project_row[0]
        try:
            test_sequence = ProcedureResult.objects.filter(unit_id = unit_id).values_list('test_sequence_definition_id',flat=True).first()
        except ProcedureResult.DoesNotExist:
            return Response({"error": "No test sequence found for this unit"}, status=status.HTTP_404)
        try:
            project = Project.objects.get(id=project_id)
            customer_id = project.customer.id
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        request_obj = request._request
        unit_url = reverse('unit-detail', args=[unit_id], request=request_obj)
        data = request.data.copy()
        data['unit'] = unit_url
        data['project_id'] = project_id
        data['customer_id'] = customer_id
        data['workorder_id'] = workorder_id
        data['test_sequence_id']=test_sequence
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
