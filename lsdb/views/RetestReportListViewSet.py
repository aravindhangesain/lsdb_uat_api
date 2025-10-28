from requests import Response
from rest_framework import viewsets
from lsdb.models import ProcedureResult,Unit
from lsdb.serializers.ProcedureResultSerializer import FailedProjectReportSerializer,RetestReportListSerializer
from django_filters import rest_framework as filters
from rest_framework_tracking.mixins import LoggingMixin
import pandas as pd
from rest_framework.decorators import action
from django.http import HttpResponse
from django.db import connection
from itertools import chain
import re
import csv
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Subquery


class RetestReportListViewSet( LoggingMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = RetestReportListSerializer
    filter_backends = [filters.DjangoFilterBackend]
    pagination_class = None

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if not start_date or not end_date:
            return ProcedureResult.objects.none() 
        # with connection.cursor() as cursor:
        #     cursor.execute("""
        #         SELECT un.unit_id 
        #         FROM lsdb_unit_notes un 
        #         JOIN lsdb_note n ON un.note_id = n.id 
        #         WHERE n.note_type_id = 3
        #     """)
        #     unit_ids = [row[0] for row in cursor.fetchall()]
        unit_ids=Unit.objects.all()
        distinct_ids = (
        ProcedureResult.objects.filter(
            stepresult__disposition_id=8,
            stepresult__measurementresult__date_time__date__range=[start_date, end_date],
        )
        .exclude(group_id=45)
        .values('id')
        .distinct())

        retest_results = ProcedureResult.objects.filter(id__in=Subquery(distinct_ids)).order_by('id')
        
        return {"retest_results": retest_results.order_by("-start_datetime")}

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        retest_results = queryset.get("retest_results", ProcedureResult.objects.none())
        return Response({
            
            "retest_results": RetestReportListSerializer(retest_results, many=True, context={'request': request}).data
        })
