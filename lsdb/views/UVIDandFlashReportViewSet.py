from rest_framework import viewsets
from lsdb.models import ProcedureResult
from lsdb.serializers import UVIDandFlashReportSerializer
from django.utils.timezone import make_aware,is_aware
import calendar
import pandas as pd
from datetime import datetime
from io import BytesIO
from django.http import HttpResponse
from rest_framework.decorators import action


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
                year, month = map(int, date_param.split("-"))
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
    
    @action(detail=False, methods=["get"])
    def download_excel(self, request):
        queryset = self.get_queryset()
        if not queryset.exists():
            return HttpResponse("No data available for the given filters", status=404)
        serializer = UVIDandFlashReportSerializer(queryset, many=True,context={'request': request})
        data = serializer.data
        df = pd.DataFrame(data)
        if "url" in df.columns:
            df.drop(columns=["url"], inplace=True)
        for col in ["start_datetime", "flash_start_datetime", "date_time"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda dt: dt.replace(tzinfo=None) if pd.notna(dt) and hasattr(dt, "utcoffset") and is_aware(dt) else dt)
        for col in ["id", "unit", "procedure_definition", "disposition", "work_order", "test_sequence_definition"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.split("/")[-2] if isinstance(x, str) and "/" in x else x)
        df.rename(columns={
            "id": "Procedure Result ID",
            "name": "Procedure Name",
            "unit": "Unit ID",
            "unit__serial_number": "Serial Number",
            "procedure_definition": "Procedure Definition ID",
            "procedure_definition__name": "Procedure Definition Name",
            "disposition": "Disposition ID",
            "disposition__name": "Disposition Name",
            "start_datetime": "Start DateTime",
            "project_number": "Project Number",
            "work_order": "WorkOrder ID",
            "work_order__name": "Work Order Name",
            "test_sequence_definition": "Test Sequence Definition ID",
            "test_sequence_definition__name": "Test Sequence Definition Name",
            "customer_name": "Customer Name",
            "flash_start_datetime": "Flash Start DateTime",
            "module_type_name": "Module Type Name",
            "stepresult__measurementresult__date_time": "Date Time"
        }, inplace=True)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="UVID_FE_Report.xlsx"'
        return response




