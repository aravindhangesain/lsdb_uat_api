from rest_framework import viewsets
from lsdb.models import ProcedureResult,Unit
from lsdb.serializers.ProcedureResultSerializer import FailedProjectReportSerializer
from datetime import timedelta
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.permissions import ConfiguredPermission
import pandas as pd
from rest_framework.decorators import action
from django.http import HttpResponse
from django.db import connection
import re
import csv


class FailedProjectReportViewSet( LoggingMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FailedProjectReportSerializer
    filter_backends = [filters.DjangoFilterBackend]
    permission_classes = [ConfiguredPermission]
    pagination_class = None

    def get_queryset(self):
        today = timezone.now().date()
        eighteen_months_ago = today - timedelta(days=18 * 30)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        queryset = ProcedureResult.objects.filter(disposition_id__in=[3, 8, 19]).distinct()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT un.unit_id 
                FROM lsdb_unit_notes un 
                JOIN lsdb_note n ON un.note_id = n.id 
                WHERE n.note_type_id = 3
            """)
            unit_ids = [row[0] for row in cursor.fetchall()]
        queryset = queryset.filter(unit_id__in=unit_ids)
        if start_date and end_date:
            queryset = queryset.filter(start_datetime__date__range=[start_date, end_date])
        else:
            queryset = queryset.filter(start_datetime__date__range=[eighteen_months_ago, today])
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[ConfiguredPermission])
    def download_csv(self, request):
        queryset = self.get_queryset()
        serializer = FailedProjectReportSerializer(queryset, many=True, context={'request': request})
        base_url = "https://lsdbwebuat.azurewebsites.net/engineering/engineering_agenda/"
        azure_file_base_url = "https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/{}/download/"
        selected_fields = ['unit_serial_number', 'project_number', 'name','customer_name','disposition_name','work_order_name',
                        'start_datetime','end_datetime','note_text','note_subject']
        data_for_csv = []
        for item in serializer.data:
            row = {field: item.get(field, '') for field in selected_fields}
            if item.get('note_id'):
                note_url = f"{base_url}{item['note_id']}"
                row['note_url'] = f'=HYPERLINK("{note_url}", "{note_url}")'
            else:
                row['note_url'] = ""
            note_id = item.get('note_id')
            image_urls = []
            if note_id:
                with connection.cursor() as cursor:
                    cursor.execute("""
                    SELECT azurefile_id 
                    FROM lsdb_note_attachments 
                    WHERE note_id = %s
                """, [note_id])
                    attachment_ids = [row[0] for row in cursor.fetchall()]
                    for azurefile_id in attachment_ids:
                        file_url = azure_file_base_url.format(azurefile_id)
                        image_urls.append(f'"{file_url}"')
            row['image_urls'] = ", ".join(image_urls) if image_urls else ""
            data_for_csv.append(row)
        df = pd.DataFrame(data_for_csv)
        html_pattern = re.compile(r'<.*?>')
        df = df.applymap(lambda x: re.sub(html_pattern, '', str(x)) if isinstance(x, str) else x)
        csv_string = df.to_csv(index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
        response = HttpResponse(csv_string, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Failed_projects_Report.csv"'
        return response
