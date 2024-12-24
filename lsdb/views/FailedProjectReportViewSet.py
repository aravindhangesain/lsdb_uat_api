from rest_framework import viewsets
from lsdb.models import ProcedureResult
from lsdb.serializers.ProcedureResultSerializer import FailedProjectReportSerializer
from datetime import datetime, timedelta
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.permissions import ConfiguredPermission
import django_filters
from django.forms.widgets import DateInput
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import action
import re
from django.http import HttpResponse


class ProcedureResultFilter(filters.FilterSet):

    start_datetime = django_filters.DateTimeFilter(
        field_name='start_datetime',
        lookup_expr='gte',
        widget=DateInput(attrs={'type': 'date'})
    )

    end_datetime = django_filters.DateTimeFilter(
        field_name='end_datetime',
        lookup_expr='lte',
        widget=DateInput(attrs={'type': 'date'})
    )

class FailedProjectReportViewSet( LoggingMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FailedProjectReportSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProcedureResultFilter
    permission_classes = [ConfiguredPermission]
    pagination_class = None

    def get_queryset(self):
        # Get today's date and 18 months ago
        today = timezone.now().date()
        eighteen_months_ago = today - timedelta(days=18 * 30)

        # Filter the queryset
        queryset = ProcedureResult.objects.filter(
            start_datetime__date__range=[eighteen_months_ago, today],
            disposition_id__in=[3, 8, 19]  # Include only specific disposition IDs
        ).distinct()

        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[ConfiguredPermission])
    def download_csv(self, request):

        # Get the queryset without filtering by customer_name
        queryset = self.get_queryset()

        # Serialize the queryset with the serializer and specify the fields
        serializer = FailedProjectReportSerializer(queryset, many=True, context={'request': request})

        # Specify the fields you want to include in the CSV
        selected_fields = ['unit_serial_number', 'project_number', 'name','customer_name','disposition_name','work_order_name',
                        'start_datetime','end_datetime']  # Replace with your desired fields
    
        # Extract data for selected fields
        data_for_csv = [{field: item[field] for field in selected_fields} for item in serializer.data]

        # Convert data to DataFrame
        df = pd.DataFrame(data_for_csv)

        # Remove HTML markup from CSV data
        html_pattern = re.compile(r'<.*?>')
        df = df.applymap(lambda x: re.sub(html_pattern, '', str(x)) if isinstance(x, str) else x)

        # Convert DataFrame to CSV string
        csv_string = df.to_csv(index=False)

        # Create HTTP response with CSV data
        response = HttpResponse(csv_string, content_type='text/csv')

        # Set filename for the downloaded CSV
        response['Content-Disposition'] = 'attachment; filename="Failed_projects_Report.csv"'
    
        return response
