from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from lsdb.models import *
from django.db.models import Prefetch
from lsdb.serializers import * 
from datetime import datetime

class AssetHistoryViewSet(viewsets.ModelViewSet):    
    queryset = ProcedureResult.objects.none()
    serializer_class = AssetHistorySerializer

    @transaction.atomic
    @action(detail=False, methods=['get', 'post'])
    def completed_units(self, request, pk=None):
        self.context = {'request': request}
        disposition = Disposition.objects.get(id=20)
        asset_id = request.query_params.get('asset_id') 
        start_date = request.query_params.get('start_date') 
        end_date = request.query_params.get('end_date')

        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        if not asset_id:
            return Response(
                {"detail": "asset_id is required in query params (?asset_id=123)."},
                status=status.HTTP_400_BAD_REQUEST
            )
        stepresult_qs = StepResult.objects.exclude(
            name__iexact="test start"
        )
        queryset = ProcedureResult.objects.filter(
            disposition=disposition,
            stepresult__measurementresult__asset__id=asset_id,
            stepresult__disposition__isnull=False
        ).prefetch_related(
            Prefetch("stepresult_set", queryset=stepresult_qs)
        ).distinct()
        if start_dt and end_dt:
            queryset = queryset.filter(
                start_datetime__gte=start_dt,
                end_datetime__lte=end_dt
            )
        serializer = AssetHistorySerializer(queryset, many=True, context=self.context)
        return Response(serializer.data, status=status.HTTP_200_OK)