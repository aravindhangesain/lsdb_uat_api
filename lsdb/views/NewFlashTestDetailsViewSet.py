import json
import uuid
import hashlib
from lsdb.models import *
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import connection, transaction
from azure.storage.blob import BlobServiceClient
from rest_framework.permissions import IsAuthenticated
from lsdb.serializers import NewFlashTestDetailsSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class NewFlashTestDetailsViewSet(viewsets.ModelViewSet):
    queryset = NewFlashTestDetails.objects.all().order_by('-date_time')
    serializer_class = NewFlashTestDetailsSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  
    
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serial_number = request.data.get("serial_number")
                date_time = request.data.get("date_time")
                json_file = request.FILES.get("json_file")
                pdf_file = request.FILES.get("pdf_file")

                if not all([serial_number, date_time, json_file, pdf_file]):
                    return Response(
                        {"error": "serial_number, date_time, json_file, and pdf_file are required."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                parsed_json = json.load(json_file)
                lsdb_payload = parsed_json.get("LSDB Payload", {})
                lsdb_payload_reference_device=lsdb_payload.get("Reference Device",{})
                procedure_result_id = lsdb_payload_reference_device.get("procedure_result_id")
                if not procedure_result_id:
                    raise Exception("procedure_result_id not found in LSDB Payload")
                
                self.update_procedure_and_step_results(procedure_result_id)
                self.update_measurement_results(procedure_result_id,parsed_json,request.user.id)
                
                original_name = json_file.name
                json_filename = f"{procedure_result_id}_{original_name}"
                json_file.seek(0)

                file_hash = self.generate_file_hash(json_file)
                json_file.seek(0)

                json_file.name = json_filename

                azure_file = AzureFile.objects.create(
                    file=json_file,
                    name=json_filename,
                    uploaded_datetime=timezone.now(),
                    hash_algorithm='sha256',
                    hash=file_hash,
                    length=json_file.size,
                    blob_container=None,
                    expires=False
                )

                measurement_result = MeasurementResult.objects.filter(step_result__procedure_result_id=procedure_result_id, name__iexact="Data file").first()
                if not measurement_result:
                    raise Exception("MeasurementResult 'Data file' not found")
                self.insert_into_resultfiles_table(measurement_result.id,azure_file.id)

                json_file.seek(0)
                self.extract_ivparams_and_save(json_file, serial_number)

                json_file.seek(0)
                azure_connection_string = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
                flash_container = 'flashfiles'
                media_container = 'media'
                blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)

                # Upload to flashfiles (PRIMARY)
                json_file.seek(0)
                flash_json_client = blob_service_client.get_blob_client(container=flash_container,blob=json_filename)
                flash_json_client.upload_blob(json_file, overwrite=True)
                json_blob_url = flash_json_client.url

                # Upload to media (BACKUP)
                json_file.seek(0)
                media_json_client = blob_service_client.get_blob_client(container=media_container,blob=json_filename)
                media_json_client.upload_blob(json_file, overwrite=True)

                # Upload to flashfiles (PRIMARY)
                pdf_filename = pdf_file.name
                pdf_blob_name = f"{uuid.uuid4()}_{pdf_filename}"
                pdf_file.seek(0)
                flash_pdf_client = blob_service_client.get_blob_client(container=flash_container,blob=pdf_blob_name)
                flash_pdf_client.upload_blob(pdf_file, overwrite=True)
                pdf_blob_url = flash_pdf_client.url

                # Upload to media (BACKUP)
                pdf_file.seek(0)
                media_pdf_client = blob_service_client.get_blob_client(container=media_container,blob=pdf_blob_name)
                media_pdf_client.upload_blob(pdf_file, overwrite=True)

                instance = NewFlashTestDetails.objects.create(
                    serial_number=serial_number,
                    procedure_result_id=procedure_result_id,
                    date_time=date_time,
                    json_file=json_filename,
                    json_file_path=json_blob_url,
                    pdf_file=pdf_filename,
                    pdf_file_path=pdf_blob_url
                )

                serializer = self.get_serializer(instance)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def update_procedure_and_step_results(self, procedure_result_id):
        try:
            current_time = timezone.now()
            disposition_id = Disposition.objects.filter(name__iexact='Requires Review').values_list('id', flat=True).first()
            ProcedureResult.objects.filter(id=procedure_result_id).update(
                disposition_id=disposition_id,
                start_datetime=current_time
            )
            StepResult.objects.filter(procedure_result_id=procedure_result_id).update(
                disposition_id=disposition_id
            )
        except Exception as e:
            raise Exception(f"Procedure/Step result update failed: {str(e)}")

    def update_measurement_results(self, procedure_result_id, parsed_json, user_id):
        try:
            current_time = timezone.now()
            disposition_id = Disposition.objects.filter(name__iexact='Completed').values_list('id', flat=True).first()
            lsdb_payload = parsed_json.get("LSDB Payload", {})
            flash_result = lsdb_payload.get("Flash Result", {})
            reference_device = lsdb_payload.get("Reference Device", {})
            asset_id = reference_device.get("Asset ID")
            if not asset_id:
                raise Exception("Asset ID missing in JSON")
            value_map = {
                "Pmp": flash_result.get("Pmp [W]"),
                "Voc": flash_result.get("Voc [V]"),
                "Vmp": flash_result.get("Vmp [V]"),
                "Isc": flash_result.get("Isc [A]"),
                "Imp": flash_result.get("Imp [A]"),
                "Irradiance": flash_result.get("Irradiance for Reporting [W/m2]"),
                "Temperature": flash_result.get("Temperature for Reporting [C]"),
            }
            step_result_ids = StepResult.objects.filter(procedure_result_id=procedure_result_id).values_list('id', flat=True)
            for name, value in value_map.items():
                if value is None:
                    continue
                MeasurementResult.objects.filter(step_result_id__in=step_result_ids,name__iexact=name).update(
                    result_double=value,
                    disposition_id=disposition_id,
                    date_time=current_time,
                    asset_id=asset_id,
                    user_id=user_id
                )
                MeasurementResult.objects.filter(step_result_id__in=step_result_ids,name__iexact="Data File").update(
                    disposition_id=disposition_id,
                    date_time=current_time,
                    user_id=user_id
                )
        except Exception as e:
            raise Exception(f"MeasurementResult update failed: {str(e)}")
            
    def generate_file_hash(self, file_data):
        hasher = hashlib.sha256()
        for buf in file_data.chunks(chunk_size=65536):
            hasher.update(buf)
        return hasher.hexdigest()
    
    def insert_into_resultfiles_table(self, measurement_result_id, azure_file_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO lsdb_measurementresult_result_files 
                (measurementresult_id, azurefile_id)
                VALUES (%s, %s)
                """,
                [measurement_result_id, azure_file_id]
            )
        
    def extract_ivparams_and_save(self, json_file, serial_number):
        try:
            parsed_json = json.load(json_file)
            iv = parsed_json.get("IVParams", {})
            v_oc_raw = iv.get("v_oc", None)
            v_oc_corr = iv.get("v_oc_corr", None)

            lsdb_payload=parsed_json.get("LSDB Payload",{})
            lsdb_payload_module_property=lsdb_payload.get("Module Property",{})
            lsdb_payload_reference_device=lsdb_payload.get("Reference Device",{})
            is_updated = lsdb_payload_module_property.get("is_updated", False)

            unit_type = Unit.objects.filter(serial_number=serial_number).values_list('unit_type_id', flat=True).first()

            point = NewFlashTestPoints.objects.create(
                serial_number=serial_number,
                v_oc_raw=v_oc_raw,
                v_oc_corr=v_oc_corr,
                spectral_mismatch=lsdb_payload_reference_device.get("Spectral MM",None),
                sweep_type=lsdb_payload_reference_device.get("sweep_type",None),
            )
            if not AdditionalModuleProperty.objects.filter(unit_type_id=unit_type).exists():
                AdditionalModuleProperty.objects.create(
                    alpha_stc_correction_a_per_c=lsdb_payload_module_property.get("alpha_stc_correction_A_per_C",None),
                    beta_stc_correction_v_per_c=lsdb_payload_module_property.get("beta_stc_correction_V_per_C",None),
                    kappa_stc_correction_ohm_per_c=lsdb_payload_module_property.get("kappa_stc_correction_Ohm_per_C",None),
                    r_s_stc_correction_ohm=lsdb_payload_module_property.get("R_s_stc_correction_Ohm",None),
                    flash_parameters=lsdb_payload_module_property.get("flash_parameters",None),
                    unit_type_id = unit_type
                )
                print("Insert completed")
            
            if is_updated:
                module_property_id = UnitType.objects.filter(id=unit_type).values_list('module_property_id', flat=True).first()
                if module_property_id:
                    ModuleProperty.objects.filter(id=module_property_id).update(
                        number_of_cells=lsdb_payload_module_property.get("number_of_cells"),
                        nameplate_pmax=lsdb_payload_module_property.get("nameplate_pmax"),
                        module_width=lsdb_payload_module_property.get("module_width"),
                        module_height=lsdb_payload_module_property.get("module_height"),
                        system_voltage=lsdb_payload_module_property.get("system_voltage"),
                        isc=lsdb_payload_module_property.get("isc"),
                        voc=lsdb_payload_module_property.get("voc"),
                        imp=lsdb_payload_module_property.get("imp"),
                        vmp=lsdb_payload_module_property.get("vmp"),
                        alpha_isc=lsdb_payload_module_property.get("alpha_isc"),
                        beta_voc=lsdb_payload_module_property.get("beta_voc"),
                        gamma_pmp=lsdb_payload_module_property.get("gamma_pmp"),
                        cells_in_series=lsdb_payload_module_property.get("cells_in_series"),
                        cells_in_parallel=lsdb_payload_module_property.get("cells_in_parallel"),
                        cell_area=lsdb_payload_module_property.get("cell_area"),
                        bifacial=bool(lsdb_payload_module_property.get("bifacial")),
                    )
                print("ModuleProperty updated")
                AdditionalModuleProperty.objects.filter(unit_type_id=unit_type).update(
                    alpha_stc_correction_a_per_c=lsdb_payload_module_property.get("alpha_stc_correction_A_per_C"),
                    beta_stc_correction_v_per_c=lsdb_payload_module_property.get("beta_stc_correction_V_per_C"),
                    kappa_stc_correction_ohm_per_c=lsdb_payload_module_property.get("kappa_stc_correction_Ohm_per_C"),
                    r_s_stc_correction_ohm=lsdb_payload_module_property.get("R_s_stc_correction_Ohm"),
                    flash_parameters=lsdb_payload_module_property.get("flash_parameters"),
                )
                print("AdditionalModuleProperty updated")
            else:
                print("is_updated = False → Only insert, no update")
            return point  
        except Exception as e:
            print("IVParams Parsing Error:", str(e))
            return None
