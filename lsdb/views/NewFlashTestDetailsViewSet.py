from rest_framework import viewsets, status
from rest_framework.response import Response
from azure.storage.blob import BlobServiceClient
from rest_framework.parsers import MultiPartParser, FormParser
import uuid
from lsdb.models import *
from lsdb.serializers import NewFlashTestDetailsSerializer
from rest_framework.permissions import IsAuthenticated
import json

class NewFlashTestDetailsViewSet(viewsets.ModelViewSet):
    queryset = NewFlashTestDetails.objects.all().order_by('-date_time')
    serializer_class = NewFlashTestDetailsSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  
    

    def create(self, request, *args, **kwargs):
        serial_number = request.data.get("serial_number")
        date_time = request.data.get("date_time")
        json_file = request.FILES.get("json_file")
        pdf_file = request.FILES.get("pdf_file")

        if not all([serial_number, date_time, json_file, pdf_file]):
            return Response(
                {"error": "serial_number, date_time, json_file_path, and pdf_file_path are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            self.extract_ivparams_and_save(json_file, serial_number)
            json_file.seek(0)

            azure_connection_string = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
            azure_container = 'flashfiles'
            blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)

            json_filename = json_file.name
            json_blob_name = f"{uuid.uuid4()}_{json_filename}"
            json_blob_client = blob_service_client.get_blob_client(container=azure_container, blob=json_blob_name)
            json_blob_client.upload_blob(json_file, overwrite=True)
            json_blob_url = json_blob_client.url

            pdf_filename = pdf_file.name
            pdf_blob_name = f"{uuid.uuid4()}_{pdf_filename}"
            pdf_blob_client = blob_service_client.get_blob_client(container=azure_container, blob=pdf_blob_name)
            pdf_blob_client.upload_blob(pdf_file, overwrite=True)
            pdf_blob_url = pdf_blob_client.url

            instance = NewFlashTestDetails.objects.create(
                serial_number=serial_number,
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
                print(module_property_id)
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
