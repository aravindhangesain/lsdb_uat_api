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
import re
from django.http import HttpResponse
from django.db import connection


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
        selected_fields = ['unit_serial_number', 'project_number', 'name','customer_name','disposition_name','work_order_name',
                        'start_datetime','end_datetime']
        data_for_csv = [{field: item[field] for field in selected_fields} for item in serializer.data]
        df = pd.DataFrame(data_for_csv)
        html_pattern = re.compile(r'<.*?>')
        df = df.applymap(lambda x: re.sub(html_pattern, '', str(x)) if isinstance(x, str) else x)
        csv_string = df.to_csv(index=False)
        response = HttpResponse(csv_string, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Failed_projects_Report.csv"'
        return response
