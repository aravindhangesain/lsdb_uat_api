import os
import hashlib
from rest_framework import viewsets, status
from rest_framework.response import Response
from azure.storage.blob import BlobServiceClient
from django.core.files.storage import default_storage
from django.conf import settings
from lsdb.serializers import FileUploadSerializer
from lsdb.models import AzureFile, ProcedureResult, StepResult, MeasurementResult
from django.db import connection
from datetime import datetime

class FileUploadViewSet(viewsets.ModelViewSet):
    serializer_class = FileUploadSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['file']
        cropped_file = serializer.validated_data['cropped_file']
        procedure_result_id = request.data.get('procedure_result_id')
        exposure_count = request.data.get('exposure_count')
        iso = request.data.get('iso')
        aperture = request.data.get('aperture')
        injection_current = request.data.get('injection_current')
        exposure_time = request.data.get('exposure_time')

        if not procedure_result_id:
            return Response({"error": "procedure_result_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        local_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

        try:
            with default_storage.open(local_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            file_hash = self.generate_file_hash(uploaded_file)
            file_size = uploaded_file.size
            file_name = uploaded_file.name

            self.upload_to_azure(local_file_path, file_name)

            azure_file = AzureFile.objects.create(
                file=file_name,
                name=file_name,
                uploaded_datetime=datetime.now(),
                hash_algorithm='sha256',
                hash=file_hash,
                length=file_size,
                blob_container=None,
                expires=False
            )
            

            procedure_result = ProcedureResult.objects.get(id=procedure_result_id)
            step_result = StepResult.objects.get(procedure_result=procedure_result)

            existing_measurement_result = MeasurementResult.objects.filter(
                step_result=step_result
            ).first()

            if existing_measurement_result is None:
                return Response({"error": "No existing MeasurementResult found for the given step result."}, 
                                status=status.HTTP_404_NOT_FOUND)

            order_value = existing_measurement_result.order
            report_order_value = existing_measurement_result.report_order  # Adjust if necessary

            self.update_measurement_result(request,step_result, 'Exposure Count', exposure_count, order_value, report_order_value, existing_measurement_result, procedure_result)
            self.update_measurement_result(request,step_result, 'ISO', iso, order_value, report_order_value, existing_measurement_result, procedure_result)
            self.update_measurement_result(request,step_result, 'Aperture', aperture, order_value, report_order_value, existing_measurement_result, procedure_result)
            self.update_measurement_result(request,step_result, 'Injection Current', injection_current, order_value, report_order_value, existing_measurement_result, procedure_result)
            self.update_measurement_result(request,step_result, 'Exposure Time', exposure_time, order_value, report_order_value, existing_measurement_result, procedure_result)

            measurement_result_el_raw = MeasurementResult.objects.filter(
                step_result=step_result,
                name="EL Image (raw)"
            ).first()

            if not measurement_result_el_raw:
                return Response({"error": "MeasurementResult with name 'EL Image (raw)' not found for the given step result."}, 
                                status=status.HTTP_404_NOT_FOUND)

            self.insert_into_resultfiles_table(measurement_result_el_raw.id, azure_file.id)

            if cropped_file:
                local_cropped_file_path = os.path.join(settings.MEDIA_ROOT, cropped_file.name)
                with default_storage.open(local_cropped_file_path, 'wb+') as destination:
                    for chunk in cropped_file.chunks():
                        destination.write(chunk)

                cropped_file_hash = self.generate_file_hash(cropped_file)
                cropped_file_size = cropped_file.size
                cropped_file_name = cropped_file.name

                self.upload_to_azure(local_cropped_file_path, cropped_file_name)

                azure_cropped_file = AzureFile.objects.create(
                    file=cropped_file_name,
                    name=cropped_file_name,
                    uploaded_datetime=datetime.now(),
                    hash_algorithm='sha256',
                    hash=cropped_file_hash,
                    length=cropped_file_size,
                    blob_container=None,
                    expires=False
                )

                measurement_result_el_grayscale = MeasurementResult.objects.filter(
                    step_result=step_result,
                    name="EL Image (grayscale)"
                ).first()

                if not measurement_result_el_grayscale:
                    return Response({"error": "MeasurementResult with name 'EL Image (grayscale)' not found for the given step result."}, 
                                    status=status.HTTP_404_NOT_FOUND)

                self.insert_into_resultfiles_table(measurement_result_el_grayscale.id, azure_cropped_file.id)

            return Response({
                "message": f"Files uploaded to local folder and Azure successfully.",
                "uploaded_file_azure_id": azure_file.id,
                "cropped_file_azure_id": azure_cropped_file.id if cropped_file else None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_file_hash(self, file_data):
        hasher = hashlib.sha256()
        for buf in file_data.chunks(chunk_size=65536):
            hasher.update(buf)
        return hasher.hexdigest()

    def upload_to_azure(self, local_file_path, file_name):
        try:
            connection_string = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
            blob_container = 'testmedia1'
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container=blob_container, blob=file_name)

            with open(local_file_path, "rb") as file_data:
                blob_client.upload_blob(file_data, overwrite=True)

            return blob_client.url

        except Exception as e:
            raise Exception(f"Error uploading file to Azure: {str(e)}")

    def update_measurement_result(self, request, step_result, name, value, order, report_order, existing_measurement_result,procedure_result):
        current_datetime = datetime.now()
        current_user = request.user.id
        if value is not None:
            measurement_result = MeasurementResult.objects.filter(
                step_result=step_result,
                name=name
            ).first()
            if measurement_result:
                if value == '':
                    measurement_result.result_double = None
                else:
                    measurement_result.result_double = value
                    
                measurement_result.asset_id = 31
                measurement_result.order = order if order is not None else measurement_result.order
                measurement_result.report_order = report_order if report_order is not None else measurement_result.report_order
                measurement_result.date_time = current_datetime
                measurement_result.user_id = current_user
                measurement_result.save()

        procedure_result.disposition_id = 13
        procedure_result.start_datetime = current_datetime
        procedure_result.save()

        step_result = StepResult.objects.filter(procedure_result=procedure_result).first()

        if step_result:
            step_result.disposition_id = 13
            step_result.start_datetime = current_datetime
            step_result.save()

        MeasurementResult.objects.filter(step_result=step_result).update(disposition_id=20,date_time=current_datetime,user_id = current_user)

    def insert_into_resultfiles_table(self, measurementresult_id, azurefile_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO lsdb_measurementresult_result_files (measurementresult_id, azurefile_id)
                VALUES (%s, %s)
                """,
                [measurementresult_id, azurefile_id]
            )

    def get_queryset(self):
        return []