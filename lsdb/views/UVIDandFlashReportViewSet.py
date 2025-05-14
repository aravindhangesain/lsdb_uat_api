from rest_framework import viewsets
from lsdb.models import ModuleProperty, ProcedureResult, Unit, UnitType
from lsdb.serializers import UVIDandFlashReportSerializer
from django.utils.timezone import is_aware
import calendar
import pandas as pd
from datetime import datetime
from io import BytesIO
from django.http import HttpResponse
from rest_framework.decorators import action


class UVIDandFlashReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UVIDandFlashReportSerializer

    def get_queryset(self):
        queryset = ProcedureResult.objects.none()
        procedure_definitions = [14, 54, 50, 62, 33, 49, 21, 38, 48]
        date_param = self.request.query_params.get("date") 
        start_date_param = self.request.query_params.get("start_date") 
        end_date_param = self.request.query_params.get("end_date")
        serial_number = self.request.query_params.get("serial_number")
        customer = self.request.query_params.get("customer")
        project = self.request.query_params.get("project")
        workorder = self.request.query_params.get("workorder")
        try:
            if start_date_param and end_date_param:
                start_date = datetime.strptime(start_date_param, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_param, "%Y-%m-%d").date()
            elif date_param:
                year, month = map(int, date_param.split("-"))
                start_date = datetime(year, month, 1).date()
                last_day = calendar.monthrange(year, month)[1]
                end_date = datetime(year, month, last_day).date()
            else:
                return queryset
            queryset = ProcedureResult.objects.filter(
                procedure_definition_id__in=procedure_definitions,
                disposition_id=2,
                stepresult__measurementresult__date_time__date__range=(start_date, end_date)
            ).distinct().order_by('-id')
            if serial_number:
                queryset = queryset.filter(unit__serial_number__icontains=serial_number)
            if customer:
                queryset = queryset.filter(work_order__project__customer__name__icontains=customer)
            if project:
                queryset = queryset.filter(work_order__project__number__icontains=project)
            if workorder:
                queryset = queryset.filter(work_order__name__icontains=workorder)
        except ValueError:
            return ProcedureResult.objects.none()
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
            unit_id = item["unit_id"]
            unit=Unit.objects.get(id=unit_id)
            unit_type = UnitType.objects.get(id=unit.unit_type_id)
            module_property=ModuleProperty.objects.get(id=unit_type.module_property_id)
            filtered_data.append({
                "Customer Name": item.get("customer_name"),
                "Project Number": item.get("project_number"),
                "Work Order Name": item.get("work_order_name"),
                "Unit Serial Number": item.get("unit_serial_number"),
                "Module Type Name": item.get("module_type_name"),
                "Procedure_Name":item.get("name"),
                "Procedure Definition Name": item.get("procedure_definition_name"),
                "Test Sequence Definition Name": item.get("test_sequence_definition_name"),
                "Flash Start DateTime": flash_start_datetime,
                "Date Time": date_time,
                "Pmp(measurement_result)": flash_values.get("Pmp", ""),
                "Voc(measurement_result)": flash_values.get("Voc", ""),
                "Vmp(measurement_result)": flash_values.get("Vmp", ""),
                "Isc(measurement_result)": flash_values.get("Isc", ""),
                "Imp(measurement_result)": flash_values.get("Imp", ""),
                "Temperature(measurement_result)": flash_values.get("Temperature", ""),
                "Irradiance(measurement_result)": flash_values.get("Irradiance", ""),
                "Pmp(stc_nameplate)": module_property.nameplate_pmax,
                "Voc(stc_nameplate)": module_property.voc,
                "Vmp(stc_nameplate)": module_property.vmp,
                "Isc(stc_nameplate)": module_property.isc,
                "Imp(stc_nameplate)": module_property.imp,
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
    

    # def get_queryset(self):
    #     queryset = ProcedureResult.objects.none()
    #     # test_sequence_ids_mapping = {
    #     #     "UVID": [255, 256, 319, 454, 475, 556],
    #     #     "FE": [11, 22, 42, 43, 132, 224, 326]
    #     # }
    #     procedure_definitions = [14, 54, 50, 62, 33, 49, 21, 38, 48]
    #     date_param = self.request.query_params.get("date") 
    #     # name = self.request.query_params.get("name")
    #     start_date_param = self.request.query_params.get("start_date") 
    #     end_date_param = self.request.query_params.get("end_date")
    #     try:
    #         if start_date_param and end_date_param:
    #             start_date = datetime.strptime(start_date_param, "%Y-%m-%d").date()
    #             end_date = datetime.strptime(end_date_param, "%Y-%m-%d").date()
    #             queryset = ProcedureResult.objects.filter(
    #                 procedure_definition_id__in=procedure_definitions,disposition_id=2,
    #                 stepresult__measurementresult__date_time__date__range=(start_date, end_date)
    #             ).distinct().order_by('-id')
    #         elif date_param:
    #             year, month = map(int, date_param.split("-"))
    #             start_date = datetime(year, month, 1).date()
    #             last_day = calendar.monthrange(year, month)[1]
    #             end_date = datetime(year, month, last_day).date()
    #             queryset = ProcedureResult.objects.filter(
    #                 procedure_definition_id__in=procedure_definitions,disposition_id=2,
    #                 stepresult__measurementresult__date_time__date__range=(start_date, end_date)
    #             ).distinct().order_by('-id')
    #     except ValueError:
    #         return queryset 
    #     return queryset
    
    # def get_filtered_data(self):
    #     ids_param = self.request.query_params.get("id") 
    #     ids = list(map(int, ids_param.split(",")))  
    #     if ids:
    #         data = ProcedureResult.objects.filter(id__in=ids)
    #         return data
    
    # @action(detail=False, methods=["get"])
    # def download_filtered_excel(self, request):
    #     queryset = self.get_filtered_data()
    #     if not queryset.exists():
    #         return HttpResponse("No data available for the given filters", status=404)
    #     serializer = UVIDandFlashReportSerializer(queryset, many=True,context={'request': request})
    #     data = serializer.data
    #     filtered_data = []
    #     for item in data:
    #         flash_values = item.get("flash_values", {})
    #         flash_start_datetime = item.get("flash_start_datetime")
    #         date_time = item.get("date_time")
    #         if isinstance(flash_start_datetime, str):
    #             flash_start_datetime = pd.to_datetime(flash_start_datetime, errors="coerce")
    #         if isinstance(date_time, str):
    #             date_time = pd.to_datetime(date_time, errors="coerce")
    #         if pd.notna(flash_start_datetime) and hasattr(flash_start_datetime, "utcoffset") and is_aware(flash_start_datetime):
    #             flash_start_datetime = flash_start_datetime.replace(tzinfo=None)
    #         if pd.notna(date_time) and hasattr(date_time, "utcoffset") and is_aware(date_time):
    #             date_time = date_time.replace(tzinfo=None) 
    #         unit_id = item["unit_id"]
    #         unit=Unit.objects.get(id=unit_id)
    #         unit_type = UnitType.objects.get(id=unit.unit_type_id)
    #         module_property=ModuleProperty.objects.get(id=unit_type.module_property_id)
    #         filtered_data.append({
    #             "Customer Name": item.get("customer_name"),
    #             "Project Number": item.get("project_number"),
    #             "Work Order Name": item.get("work_order_name"),
    #             "Unit Serial Number": item.get("unit_serial_number"),
    #             "Module Type Name": item.get("module_type_name"),
    #             "Procedure_Name":item.get("name"),
    #             "Procedure Definition Name": item.get("procedure_definition_name"),
    #             "Test Sequence Definition Name": item.get("test_sequence_definition_name"),
    #             "Flash Start DateTime": item.get("flash_start_datetime"),
    #             "Date Time": item.get("date_time"),
    #             "Pmp(measurement_result)": flash_values.get("Pmp", ""),
    #             "Voc(measurement_result)": flash_values.get("Voc", ""),
    #             "Vmp(measurement_result)": flash_values.get("Vmp", ""),
    #             "Isc(measurement_result)": flash_values.get("Isc", ""),
    #             "Imp(measurement_result)": flash_values.get("Imp", ""),
    #             "Temperature(measurement_result)": flash_values.get("Temperature", ""),
    #             "Irradiance(measurement_result)": flash_values.get("Irradiance", ""),
    #             "Pmp(stc_nameplate)": module_property.nameplate_pmax,
    #             "Voc(stc_nameplate)": module_property.voc,
    #             "Vmp(stc_nameplate)": module_property.vmp,
    #             "Isc(stc_nameplate)": module_property.isc,
    #             "Imp(stc_nameplate)": module_property.imp,
    #         })
    #     df = pd.DataFrame(filtered_data)
    #     for col in ["Flash Start DateTime", "Date Time"]:
    #         if col in df.columns:
    #             df[col] = df[col].apply(lambda dt: dt.replace(tzinfo=None) if pd.notna(dt) and hasattr(dt, "utcoffset") and is_aware(dt) else dt)
    #     output = BytesIO()
    #     with pd.ExcelWriter(output, engine="openpyxl") as writer:
    #         df.to_excel(writer, index=False, sheet_name="Report")
    #     output.seek(0)
    #     response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    #     response["Content-Disposition"] = f'attachment; filename="UVID_FE_Report.xlsx"'
    #     return response
