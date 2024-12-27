from rest_framework import serializers
from django.db.models import Q
import json
import magic
import pandas as pd
from azure.storage.blob import BlobServiceClient
from lsdb.models import MeasurementResult_pichina, ProcedureResult_FinalResult_pichina, ProcedureResult_pichina
from lsdb.serializers import UnitType_pichinaSerializer


class TransformIVCurve_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    # test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    # disposition_name = serializers.SerializerMethodField()
    # visualizer = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')
    unit_type = UnitType_pichinaSerializer(source='unit.unit_type', many=False)
    flash_values = serializers.SerializerMethodField()
    iv_curves = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()
    # multiplier = serializers.SerializerMethodField()
    # has_notes = serializers.SerializerMethodField()
    # open_notes = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()

    # def get_has_notes(self, obj):
    #     if obj.notes.count() > 0:
    #         return True
    #     else:
    #         return False

    def get_final_result(self, instance):
        try:
            final_result_value = ProcedureResult_FinalResult_pichina.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult_pichina.DoesNotExist:
            return None

    # def get_open_notes(self, obj):
    #     if obj.notes.filter(Q(disposition__complete=False) | Q(disposition__isnull=True)).count() > 0:
    #         return True
    #     else:
    #         return False

    def get_multiplier(self, obj):
        # Stubbed deliberately --MD
        # print('in mult')
        # flash_measurements = MeasurementResult.objects.filter(
        #     step_result__in=obj.stepresult_set.all(),
        #     measurement_result_type__name__icontains='result_double'
        # )
        flash = {}
        # for measurement in flash_measurements:
        #     flash[measurement.name] = measurement.result_double
        return (flash)

    def get_flash_values(self, obj):
        # print('in flash')
        # TODO: This should suppress failing measurements
        flash_measurements = MeasurementResult_pichina.objects.filter(
            step_result__in=obj.stepresult_pichina_set.all(),
            measurement_result_type__name__icontains='result_double'
        )
        flash = {}
        for measurement in flash_measurements:
            flash[measurement.name] = measurement.result_double
        return (flash)

    def parse_flash(self, blob_client):
        """
        Parses the uploaded file and returns raw data.
        """
        try:
            file_handle = blob_client.download_blob().readall()
            if magic.from_buffer(file_handle[:2048], mime=True) != 'text/plain':
                 return None
            raw_data = [line.strip() for line in file_handle.decode('utf-8').splitlines()]
            return raw_data
        
        except Exception as e:
            print(f"Error parsing file: {e}")
            return None

    def get_iv_curves(self, obj):
        """
        Processes measurement data to generate IV curves.
        """
        AZURE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
        CONTAINER_NAME = 'testmedia1'
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        measurements = MeasurementResult_pichina.objects.filter(
            step_result__in=obj.stepresult_pichina_set.all(),
            measurement_result_type__name__icontains='result_files',
            disposition__isnull=False
        ).exclude(
            disposition__name__icontains='fail'
        )
        iv_curves = [{
            'id': 0,
            'multiplier': 1,
            "color": "hsl(263, 70%, 50%)",
            "chart": [{"x": 0, "y": 0}]
        }]
        try:
            for measurement in measurements:
                if measurement.result_files.all().count() == 1:  
                    curve_dict = {}
                    curve_dict['id'] = measurement.id
                    curve_dict['color'] = "hsl(263, 70%, 50%)"
                    curve_dict['multiplier'] = 0
                    file_instance = measurement.result_files.first()
                    blob_name = file_instance.file
                    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
                    raw_data = self.parse_flash(blob_client)
                    if raw_data is None:
                        raise ValueError("Failed to parse the file.")
                    points_indices = [i for i, line in enumerate(raw_data) if 'Points' in line]
                    if len(points_indices) < 3:
                        raise ValueError("The file does not contain a third 'Points' section.")
                    start_index = points_indices[2] + 2  
                    header_line = raw_data[start_index] 
                    data_lines = raw_data[start_index + 2:]  
                    columns = header_line.split(';')
                    parsed_data = [line.split(';') for line in data_lines if line.strip()]
                    data_section = pd.DataFrame(parsed_data, columns=columns)
                    data_section.columns = data_section.columns.str.strip()  
                    relevant_data = data_section.iloc[:, [2, 3]]  
                    relevant_data.columns = ["Voltage", "Current"]
                    relevant_data["Voltage"] = pd.to_numeric(relevant_data["Voltage"], errors='coerce')
                    relevant_data["Current"] = pd.to_numeric(relevant_data["Current"], errors='coerce')
                    relevant_data = relevant_data.dropna()
                    chart_array = {
                        "id": measurement.id,
                        "multiplier": 0.99887,
                        "color": "hsl(263, 70%, 50%)",
                        "chart": [
                            {"x": row["Voltage"], "y": row["Current"]}
                            for _, row in relevant_data.iterrows()
                        ],
                    }
                    iv_curves.append(chart_array)
        except Exception as e:
            print(e)
            print(f"Error processing measurement: {e}")
            iv_curves.append(
                {
                    'id': 0,
                    'multiplier': 1,
                    "color": "hsl(263, 70%, 50%)",
                    "chart": [{"x": 0, "y": 0}]
                }
            )
        return iv_curves

    def get_disposition_name(self, obj):
        # print('in disp')
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_assets(self, obj):
        measurements = MeasurementResult_pichina.objects.filter(
            step_result__in=obj.stepresult_pichina_set.all(),
            disposition__isnull=False,
        ).distinct().values_list('asset__name')
        assets = set(measurements)
        return assets

    class Meta:
        model = ProcedureResult_pichina
        fields = [
            'id',
            'url',
            'unit',
            'procedure_definition_name',
            'disposition',
            'name',
            'unit_type',
            'flash_values',
            'iv_curves',
            'assets',
            # 'has_notes',
            # 'open_notes',
            'final_result'
        ]