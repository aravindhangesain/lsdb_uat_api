from rest_framework import viewsets
from lsdb.models import ProcedureResult
from lsdb.serializers import UVIDandFlashReportSerializer
from django.utils.timezone import make_aware
import calendar
from datetime import datetime


class UVIDandFlashReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UVIDandFlashReportSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = ProcedureResult.objects.none()  
        test_sequence_ids_mapping = {
            "UVID": [255, 256, 319, 454, 475, 556],
            "FE": [11, 22, 42, 43, 132, 224, 326]
        }
        procedure_definitions = [14, 54, 50, 62, 33, 49, 21, 38, 48]
        date_param = self.request.query_params.get("date") 
        name = self.request.query_params.get("name")
        if not date_param or not name:
            return queryset 
        name = name.upper()
        if name in test_sequence_ids_mapping:
            try:
                month, year = map(int, date_param.split("-"))
                last_day = calendar.monthrange(year, month)[1]
                start_date = make_aware(datetime(year, month, 1))  
                end_date = make_aware(datetime(year, month, last_day))
                test_sequence_ids = test_sequence_ids_mapping[name]
                queryset = ProcedureResult.objects.filter(
                    test_sequence_definition_id__in=test_sequence_ids,
                    procedure_definition_id__in=procedure_definitions,
                    stepresult__measurementresult__date_time__range=(start_date, end_date)
                    ).distinct()
                # print(queryset.query)
            except ValueError:
                return queryset
        return queryset



