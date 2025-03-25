from requests import Response
from rest_framework import viewsets
from lsdb.models import ProcedureResult,Unit
from lsdb.serializers.ProcedureResultSerializer import FailedProjectReportSerializer
from django_filters import rest_framework as filters
from rest_framework_tracking.mixins import LoggingMixin
import pandas as pd
from rest_framework.decorators import action
from django.http import HttpResponse
from django.db import connection
import re
import csv
from rest_framework.response import Response
from django.db.models import Q

class FailedProjectReportViewSet( LoggingMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = FailedProjectReportSerializer
    filter_backends = [filters.DjangoFilterBackend]
    pagination_class = None

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if not start_date or not end_date:
            return ProcedureResult.objects.none()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT un.unit_id 
                FROM lsdb_unit_notes un 
                JOIN lsdb_note n ON un.note_id = n.id 
                WHERE n.note_type_id = 3
            """)
            unit_ids = [row[0] for row in cursor.fetchall()]
        queryset1 = ProcedureResult.objects.filter(
            disposition_id__in=[3, 8, 19],
            unit_id__in=unit_ids,
            start_datetime__date__range=[start_date, end_date]
        ).distinct()
        excluded_units = Unit.objects.filter(
            Q(notes__subject__icontains="Quality issue") |
            Q(notes__subject__icontains="Mishandling damage") |
            Q(notes__subject__icontains="Pull Request")
        ).values_list("id", flat=True)
        queryset2 = ProcedureResult.objects.filter(
            disposition_id=2
        ).exclude(
            unit_id__in=excluded_units
        ).filter(
            unit__notes__note_type_id=3,
            start_datetime__date__range=[start_date, end_date]
        )
        combined_queryset = queryset1.union(queryset2).order_by("-start_datetime")
        return combined_queryset

    @action(detail=False, methods=['get'],)
    def download_csv(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        unit_ids = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT un.unit_id 
                FROM lsdb_unit_notes un 
                JOIN lsdb_note n ON un.note_id = n.id 
                WHERE n.note_type_id = 3
            """)
            unit_ids = [row[0] for row in cursor.fetchall()]
        queryset1 = ProcedureResult.objects.filter(
            disposition_id__in=[3, 8, 19],
            unit_id__in=unit_ids,
            start_datetime__date__range=[start_date, end_date]
        ).distinct()
        procedure_ids_param = request.query_params.get('procedure_ids', '')
        pass_ids = [pid.strip() for pid in procedure_ids_param.split(',') if pid.strip().isdigit()]
        if pass_ids:
            queryset2 = ProcedureResult.objects.filter(id__in=pass_ids)
            custom_queryset = queryset1.union(queryset2)
        else:
            custom_queryset = queryset1.exclude(id__in=pass_ids) 
        serializer = FailedProjectReportSerializer(custom_queryset, many=True, context={'request': request})
        base_url = "https://lsdbwebuat.azurewebsites.net/engineering/engineering_agenda/"
        azure_file_base_url = "https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/{}/download/"
        selected_fields = ['unit_serial_number', 'project_number', 'name','customer_name','disposition_name','work_order_name',
                        'start_datetime','end_datetime','note_subject','note_text']
        data_for_csv = []
        for item in serializer.data:
            row = {field: item.get(field, '') for field in selected_fields}
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
            if note_id:
                note_url = f"{base_url}{note_id}"
                row['flag_redirect_url'] = f'=HYPERLINK("{note_url}", "{note_url}")'
            else:
                row['flag_redirect_url'] = ""
            data_for_csv.append(row)
        df = pd.DataFrame(data_for_csv)
        html_pattern = re.compile(r'<.*?>')
        df = df.applymap(lambda x: re.sub(html_pattern, '', str(x)) if isinstance(x, str) else x)
        desired_order = selected_fields[:selected_fields.index('note_text') + 1] + ['image_urls', 'flag_redirect_url'] + selected_fields[selected_fields.index('note_text') + 1:]
        df = df[desired_order]
        csv_string = df.to_csv(index=False, encoding='utf-8', quoting=csv.QUOTE_ALL)
        response = HttpResponse(csv_string, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Failed_projects_Report.csv"'
        return response
    
    