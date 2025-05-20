from rest_framework import viewsets
from lsdb.models import AzureFile, MeasurementResult, ModuleProperty, OldMeasurementResult, ProcedureResult, Unit, UnitType
from lsdb.serializers import UVIDandFlashReportSerializer
from django.utils.timezone import is_aware
import calendar
import pandas as pd
from datetime import datetime
from io import BytesIO
from django.http import HttpResponse
from rest_framework.decorators import action
import pandas as pd
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from azure.storage.blob import BlobServiceClient
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import pandas as pd
import tempfile
import os
import math






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
            # module_nameplate=item.get("module_nameplate",{})
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
                "Procedure Result ID": item.get("id"),
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
                "Imp(stc_nameplate)": module_property.imp
                # "Imp_deviation":module_nameplate.get("Imp"),
                # "Pmp_deviation":module_nameplate.get("Pmp"),
                # "Vmp_deviation":module_nameplate.get("Vmp"),
                # "Voc_deviation":module_nameplate.get("Voc"),
                # "Isc_deviation":module_nameplate.get("Isc")


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
    
    @action(detail=False, methods=['get', 'post'], url_path='correction_factor_file_upload')
    def correction_factor_file_upload(self, request):
        azure_file_id = request.data.get('azure_file_id')

        if not azure_file_id:
            return Response({'error': 'Missing `azure_file_id` in request data'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            azurefile = AzureFile.objects.get(id=azure_file_id)
        except AzureFile.DoesNotExist:
            return Response({'error': 'Invalid `azure_file_id`'}, status=status.HTTP_400_BAD_REQUEST)

        file_name = azurefile.name

        if not file_name:
            return Response({'error': 'Missing `filename` in AzureFile record'}, status=status.HTTP_400_BAD_REQUEST)

        connect_str = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
        container_name = 'media'

        try:
            # Connect to Azure Blob
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            container_client = blob_service_client.get_container_client(container_name)

            # Check if blob exists
            blob_list = list(container_client.list_blobs(name_starts_with=file_name))
            if not blob_list:
                return Response({'error': f'File `{file_name}` not found in Azure Blob Storage'}, status=status.HTTP_404_NOT_FOUND)

            blob_client = container_client.get_blob_client(file_name)

            # Download blob to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
                download_stream = blob_client.download_blob()
                tmp_file.write(download_stream.readall())
                tmp_file_path = tmp_file.name

            # Read the Excel file
            df = pd.read_excel(tmp_file_path)

            # Clean up temp file
            os.unlink(tmp_file_path)

            required_columns = [
                'Procedure Result ID',
                'Pmp(measurement_result)',
                'Voc(measurement_result)',
                'Vmp(measurement_result)',
                'Isc(measurement_result)',
                'Imp(measurement_result)'
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response({'error': f'Missing columns: {missing_columns}'}, status=status.HTTP_400_BAD_REQUEST)

            old_saved_count = 0
            updated_count = 0
            skipped = []

            for _, row in df.iterrows():
                procedure_result_id = row['Procedure Result ID']
                try:
                    procedure_result = ProcedureResult.objects.get(id=procedure_result_id)
                except ProcedureResult.DoesNotExist:
                    skipped.append({'procedure_result_id': procedure_result_id, 'reason': 'Not found'})
                    continue

                # Fetch existing results
                measurement_results = MeasurementResult.objects.filter(
                    step_result__procedure_result=procedure_result,
                    name__in=["Imp", "Isc", "Vmp", "Voc", "Pmp"]
                )

                result_dict = {mr.name: mr for mr in measurement_results}
                existing_values = {
                    'Imp': result_dict.get('Imp').result_double if result_dict.get('Imp') else None,
                    'Isc': result_dict.get('Isc').result_double if result_dict.get('Isc') else None,
                    'Vmp': result_dict.get('Vmp').result_double if result_dict.get('Vmp') else None,
                    'Voc': result_dict.get('Voc').result_double if result_dict.get('Voc') else None,
                    'Pmp': result_dict.get('Pmp').result_double if result_dict.get('Pmp') else None,
                }

                new_values = {
                    key: None if pd.isnull(row[f"{key}(measurement_result)"]) else row[f"{key}(measurement_result)"]
                    for key in ['Imp', 'Isc', 'Vmp', 'Voc', 'Pmp']
                }

                # Check if any value has changed
                any_changed = False
                for key in existing_values:
                    old_val = existing_values[key]
                    new_val = new_values[key]
                    if old_val != new_val:
                        if old_val is None or new_val is None:
                            any_changed = True
                            break
                        if not math.isclose(old_val, new_val, rel_tol=1e-9):
                            any_changed = True
                            break

                if any_changed:
                    # Save old values
                    OldMeasurementResult.objects.create(
                        procedure_result=procedure_result,
                        imp=existing_values['Imp'],
                        isc=existing_values['Isc'],
                        vmp=existing_values['Vmp'],
                        voc=existing_values['Voc'],
                        pmp=existing_values['Pmp']
                    )
                    old_saved_count += 1

                    # Update changed values
                    for key, new_val in new_values.items():
                        measurement = result_dict.get(key)
                        if measurement:
                            old_val = measurement.result_double
                            if old_val != new_val:
                                if old_val is None or new_val is None or not math.isclose(old_val, new_val, rel_tol=1e-9):
                                    measurement.result_double = new_val
                                    measurement.reviewed_by_user_id = request.user.id
                                    measurement.save()
                                    updated_count += 1

            return Response({
                'message': 'Correction factors uploaded and applied successfully.',
                'old_measurements_saved': old_saved_count,
                'measurement_results_updated': updated_count,
                'skipped': skipped
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
