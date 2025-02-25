import os
from rest_framework import viewsets
from rest_framework.decorators import action
from datetime import datetime
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from lsdb.models import AzureFile, MeasurementResult, StepResult, ProcedureResult, TestSequenceDefinition, Unit, WorkOrder
from lsdb.serializers import FileUploadforFlashSerializer
from azure.storage.blob import BlobServiceClient
import hashlib
from django.db import connection
import logging
import pandas as pd

class FileUploadforFlashViewSet(viewsets.ModelViewSet):
    serializer_class = FileUploadforFlashSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = serializer.validated_data['file']
        procedure_result_id = request.data.get('procedure_result_id')

        if not procedure_result_id:
            return Response({"error": "procedure_result_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        local_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)

        try:
            step_result = StepResult.objects.filter(procedure_result_id=procedure_result_id).first()
            if not step_result:
                return Response({"error": "StepResult not found for the given procedure_result_id."}, status=status.HTTP_400_BAD_REQUEST)

            measurement_result = MeasurementResult.objects.filter(step_result_id=step_result.id).first()
            if not measurement_result:
                return Response({"error": "MeasurementResult not found for the given step_result_id."}, status=status.HTTP_400_BAD_REQUEST)

            existing_file = self.check_existing_file(measurement_result.id)
            if existing_file:
                return Response({"message": "File already uploaded for this MeasurementResult."}, status=status.HTTP_200_OK)

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

            current_user = request.user.id
            current_datetime = datetime.now()
            step_result_ids = StepResult.objects.filter(procedure_result_id=procedure_result_id).values_list('id', flat=True)
            measurement_result_ids = MeasurementResult.objects.filter(step_result_id__in=step_result_ids).values_list('id', flat=True)
            MeasurementResult.objects.filter(id__in=measurement_result_ids).update(user_id=current_user)
            MeasurementResult.objects.filter(id__in=measurement_result_ids).update(date_time=current_datetime)
            ProcedureResult.objects.filter(id=procedure_result_id).update(disposition_id=13)
            StepResult.objects.filter(id__in=step_result_ids).update(disposition_id=13)
            MeasurementResult.objects.filter(step_result_id__in=step_result_ids).update(disposition_id=20, asset_id=9)
            data_file_entry = MeasurementResult.objects.filter(step_result_id__in=step_result_ids, name="Data File").first()
            csv_update_response = self.update_from_csv(local_file_path,procedure_result_id)
            if 'error' in csv_update_response:
                return Response(csv_update_response, status=status.HTTP_400_BAD_REQUEST)
            if data_file_entry:
                measurement_result_id = data_file_entry.id

                self.insert_into_resultfiles_table(measurement_result_id, azure_file.id)
            
            # self.handle_test_sequence_logic(procedure_result_id)

            return Response({"success": "File uploaded and data updated successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def check_existing_file(self, measurement_result_id):
        # Check if the measurement_result_id already exists in the MeasurementResultResultFiles table
        query = """
        SELECT 1 FROM lsdb_measurementresult_result_files
        WHERE measurementresult_id = %s
        LIMIT 1
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [measurement_result_id])
            return cursor.fetchone()
        
    def handle_test_sequence_logic(self, procedure_result_id):
        try:
            procedure_result = ProcedureResult.objects.filter(id=procedure_result_id).first()
            if not procedure_result:
                raise Exception("ProcedureResult not found.")

            test_sequence = procedure_result.test_sequence_definition
            if not test_sequence:
                raise Exception("TestSequence not found for ProcedureResult.")
            
            control_sequence = TestSequenceDefinition.objects.filter(name__icontains="Control").first()
            control_id = control_sequence.id
            if test_sequence.id == control_id:
                unit_id=ProcedureResult.objects.filter(id=procedure_result_id).values_list('unit_id',flat=True).first()
                procedure_definition_id = ProcedureResult.objects.filter(id=procedure_result_id).values_list('procedure_definition_id',flat=True).first()
                if procedure_definition_id:
                    if ProcedureResult.objects.filter(unit_id=unit_id,procedure_definition_id=procedure_definition_id).count()==1:
                        self.build_bucket(procedure_result.work_order.id, procedure_result.unit.id, test_sequence)

        except Exception as e:
            raise Exception(f"Error in handling test sequence logic: {str(e)}")
        
    def build_bucket(self, work_order_id, unit_id,test_sequence):
        unit_instance = Unit.objects.get(id=unit_id)
        work_order_instance = WorkOrder.objects.get(id=work_order_id)
        for execution in test_sequence.procedureexecutionorder_set.all():
            if execution.execution_condition:
                ldict = {'unit': unit_instance, 'retval': False}
                exec('retval={}'.format(execution.execution_condition), None, ldict)
                if not ldict['retval']:
                    continue

            for _ in range(4):  
                procedure_result = ProcedureResult.objects.create(
                    unit=unit_instance,
                    name=execution.execution_group_name,
                    disposition=None,
                    work_order=work_order_instance,
                    group=execution.procedure_definition.group,
                    procedure_definition=execution.procedure_definition,
                    version=execution.procedure_definition.version,
                    linear_execution_group=execution.execution_group_number,
                    test_sequence_definition=test_sequence,
                    allow_skip=execution.allow_skip,
                )

                for step_execution in execution.procedure_definition.stepexecutionorder_set.all():
                    step_result = StepResult.objects.create(
                        name=step_execution.execution_group_name,
                        procedure_result=procedure_result,
                        step_definition=step_execution.step_definition,
                        execution_number=0,
                        disposition=None,
                        start_datetime=None,
                        duration=0,
                        test_step_result=None,
                        archived=False,
                        description=None,
                        step_number=0,
                        step_type=step_execution.step_definition.step_type,
                        linear_execution_group=step_execution.execution_group_number,
                        allow_skip=step_execution.allow_skip,
                    )
                    for measurement_definition in step_execution.step_definition.measurementdefinition_set.all():
                        MeasurementResult.objects.create(
                            step_result=step_result,
                            measurement_definition=measurement_definition,
                            software_revision=0.0,
                            disposition=None,
                            limit=measurement_definition.limit,
                            station=0,
                            name=measurement_definition.name,
                            record_only=measurement_definition.record_only,
                            allow_skip=measurement_definition.allow_skip,
                            requires_review=measurement_definition.requires_review,
                            measurement_type=measurement_definition.measurement_type,
                            order=measurement_definition.order,
                            report_order=measurement_definition.report_order,
                            measurement_result_type=measurement_definition.measurement_result_type,
                        )

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
        
    def insert_into_resultfiles_table(self, measurement_result_id, azure_file_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO lsdb_measurementresult_result_files (measurementresult_id, azurefile_id)
                VALUES (%s, %s)
                """,
                [measurement_result_id, azure_file_id]
            )

    def update_from_csv(self, local_file_path, procedure_result_id):
        try:
            
            with open(local_file_path, 'r', encoding='utf-8') as file:
                raw_content = file.readlines()

            for index, line in enumerate(raw_content):
                if "CellParamArea;Tcell;" in line:
                    tcell_header_index = index
                    tcell_value_index = index + 1
                    break
            else:
                return {"error": "Tcell header not found in the file."}

           
            tcell_header = raw_content[tcell_header_index].strip().split(';')
            tcell_data = raw_content[tcell_value_index].strip().split(';')\

            row_5 = raw_content[4].strip()  
            row_7 = raw_content[6].strip()
            row_5_columns = row_5.split(';')
            row_7_columns = row_7.split(';')

            if "Tcell" in row_5_columns:
                tcell_index = row_5_columns.index("Tcell")
                tcell_value_raw = row_7_columns[tcell_index]

                

                try:
                    tcell_value = float(tcell_value_raw)
                except ValueError:
                    return {"error": f"Failed to convert Tcell value to float: '{tcell_value_raw}'."}
            else:
                return {"error": "Tcell column not found in the file."}

            # Locate ISC-related data
            isc_data_start = next(
                (index for index, line in enumerate(raw_content) if 'Isc;Uoc;Impp;Umpp;Pmpp' in line), None
            )

            if isc_data_start is None:
                return {"error": "ISC header not found in the file."}

            
            isc_header = raw_content[isc_data_start].strip().split(';')
            isc_data = raw_content[isc_data_start + 2:]  # Data rows after header and units
            isc_rows = [line.strip().split(';') for line in isc_data if line.strip()]
            isc_df = pd.DataFrame(isc_rows, columns=isc_header)

            
            field_mapping = {
                "Isc": "Isc",
                "Voc": "Uoc",
                "Imp": "Impp",
                "Vmp": "Umpp",
                "Pmp": "Pmpp",
                "Irradiance": "Insol",
            }

            
            procedure_result = ProcedureResult.objects.get(id=procedure_result_id)
            stepresult = StepResult.objects.filter(procedure_result_id=procedure_result).values_list('id', flat=True)

            
            for db_field_name, csv_column in field_mapping.items():
                if csv_column in isc_df.columns:
                    value = isc_df[csv_column].iloc[0]  # Get the first row's value
                    if not value:
                        return {"error": f"Invalid or empty {csv_column} value in CSV."}

                    try:
                        value = float(value)
                    except ValueError:
                        return {"error": f"Failed to convert {csv_column} value to float: '{value}'."}

                    MeasurementResult.objects.filter(
                        step_result_id__in=stepresult, name=db_field_name
                    ).update(result_double=value)

            MeasurementResult.objects.filter(
                step_result_id__in=stepresult, name="Temperature"
            ).update(result_double=tcell_value)

            return {"success": "Data successfully updated from CSV file, including Tcell."}
        except Exception as e:
            logging.error(f"Error while processing CSV file: {str(e)}")
            return {"error": f"An error occurred while processing the CSV file: {str(e)}"}
        

    def get_queryset(self):
        return []





