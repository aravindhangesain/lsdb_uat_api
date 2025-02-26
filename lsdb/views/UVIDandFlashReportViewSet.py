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
        filtered_data = []
        for item in data:
            flash_values = item.get("flash_values", {})
            flash_start_datetime = item.get("flash_start_datetime")
            date_time = item.get("date_time")
            if isinstance(flash_start_datetime, str):
                flash_start_datetime = pd.to_datetime(flash_start_datetime, errors="coerce")
            if isinstance(date_time, str):
                date_time = pd.to_datetime(date_time, errors="coerce")
            if pd.notna(flash_start_datetime) and hasattr(flash_start_datetime, "utcoffset") and is_aware(flash_start_datetime):
                flash_start_datetime = flash_start_datetime.replace(tzinfo=None)
            if pd.notna(date_time) and hasattr(date_time, "utcoffset") and is_aware(date_time):
                date_time = date_time.replace(tzinfo=None)
            filtered_data.append({
                "Customer Name": item.get("customer_name"),
                "Project Number": item.get("project_number"),
                "Work Order Name": item.get("work_order_name"),
                "Unit Serial Number": item.get("unit_serial_number"),
                "Module Type Name": item.get("module_type_name"),
                "Procedure Definition Name": item.get("procedure_definition_name"),
                "Test Sequence Definition Name": item.get("test_sequence_definition_name"),
                "Flash Start DateTime": item.get("flash_start_datetime"),
                "Date Time": item.get("date_time"),
                "Pmp": flash_values.get("Pmp", ""),
                "Voc": flash_values.get("Voc", ""),
                "Vmp": flash_values.get("Vmp", ""),
                "Isc": flash_values.get("Isc", ""),
                "Imp": flash_values.get("Imp", ""),
            })
        df = pd.DataFrame(filtered_data)
        for col in ["Flash Start DateTime", "Date Time"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda dt: dt.replace(tzinfo=None) if pd.notna(dt) and hasattr(dt, "utcoffset") and is_aware(dt) else dt)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="UVID_FE_Report.xlsx"'
        return response




