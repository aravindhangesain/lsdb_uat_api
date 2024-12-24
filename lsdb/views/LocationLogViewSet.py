from django.db import connection
from rest_framework import viewsets
from lsdb.models import LocationLog,Unit
from lsdb.serializers import LocationLogSerializer
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from datetime import datetime, timedelta
import csv


class LocationLogFilter(filters.FilterSet):
    flag=filters.NumberFilter()
    class Meta:
        model = LocationLog
        fields = ['flag']


class LocationLogViewSet(viewsets.ModelViewSet):
    queryset=LocationLog.objects.all()
    serializer_class=LocationLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LocationLogFilter
    lookup_field='serial_number'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        custom_data = {
            'location_log': serializer.data
        }
        return Response(custom_data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='unit_history')
    def unit_history(self, request, serial_number=None):
        unit = Unit.objects.filter(serial_number=serial_number).first()
        if unit:
            location_history = LocationLog.objects.filter(unit_id=unit.id, flag__in=[1, 3])
            serialized_data = LocationLogSerializer(location_history, many=True).data
            return Response(serialized_data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Unit not found."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], url_path='unit_history/download_csv')
    def download_csv(self, request, serial_number=None):
        unit = Unit.objects.filter(serial_number=serial_number).first()
        if not unit:
            return Response({"detail": "Unit not found."}, status=status.HTTP_404_NOT_FOUND)
        
        location_history = LocationLog.objects.filter(unit_id=unit.id, flag__in=[1, 3])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="unit_history_{serial_number}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Location ID', 'Project ID', 'Unit ID', 'Datetime', 'Is Latest', 'Flag', 'Asset ID', 'Username'])

        for log in location_history:
            writer.writerow([
                log.id,
                log.location_id,
                log.project_id,
                log.unit_id,
                log.datetime,
                log.is_latest,
                log.flag,
                log.asset_id,
                log.username
            ])

        return response

    @action(detail=False, methods=['get'], url_path='between-dates')
    def get_logs_between_dates(self, request):
        """
        Endpoint to retrieve filtered logs in JSON format.
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {'error': 'Both start_date and end_date are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

            logs = self.queryset.filter(
                datetime__gte=start_date,
                datetime__lt=end_date,
                location_id__in=[10, 11]
            )

            if not logs.exists():
                return Response(
                    {'error': 'No data found for the given date range.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='between-dates/download')
    def download_logs_between_dates(self, request):
        """
        Endpoint to download filtered logs as a CSV file.
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {'error': 'Both start_date and end_date are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert end_date to include the full day
            end_date = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

            logs = self.queryset.filter(
                datetime__gte=start_date,
                datetime__lt=end_date,
                location_id__in=[10, 11]
            )

            if not logs.exists():
                return Response(
                    {'error': 'No data found for the given date range.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Generate CSV file
            return self.generate_csv_response(logs)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def generate_csv_response(self, logs):
        """
        Generate a CSV response from a queryset of logs.
        """
        # Create an HTTP response with CSV content type
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="location_logs.csv"'

        # Create a CSV writer object
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Unit ID', 'Serial Number','Datetime', 'Location', 'Username', 'Project Number','Flag', 'Is Latest'])

        project_numbers = {}

        # Write rows for each log entry
        for log in logs:
            unit_id = log.unit_id
            if unit_id not in project_numbers:
                project_numbers[unit_id]=self.get_project_number(unit_id)
            project_number = project_numbers[unit_id]
            writer.writerow([
                log.unit_id,
                log.unit.serial_number if log.unit else '', 
                log.datetime,
                log.location,
                log.username,
                project_number,
                log.flag,
                log.is_latest
            ])

        return response
    

    def get_project_number(self, unit_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.number
                FROM lsdb_project_units pu
                INNER JOIN lsdb_project p ON pu.project_id = p.id
                WHERE pu.unit_id = %s
            """, [unit_id])
            result = cursor.fetchone()
        return result[0] if result else ''