from rest_framework import serializers
from lsdb.models import ProcedureResult, Unit, UnitType, ModuleProperty, MeasurementResult,AzureFile,ProcedureDefinition
from lsdb.serializers import AzureFileSerializer

class GetDeliverablesDataSerializer(serializers.ModelSerializer):
    const_rows = serializers.SerializerMethodField()

    def get_const_rows(self, obj):
        # Ensure we're working with the actual ProcedureResult instance
        if isinstance(obj, ProcedureResult):
            unit = Unit.objects.filter(id=obj.unit_id).first()
            if not unit:
                return []  

            unittype = UnitType.objects.filter(id=unit.unit_type_id).first()
            if not unittype:
                return []  

            moduleproperty = ModuleProperty.objects.filter(id=unittype.id).first()
            if not moduleproperty:
                return []  
            measurements = MeasurementResult.objects.filter(step_result__procedure_result=obj.id)
            result_dict = {measurement.name: measurement.result_double for measurement in measurements}

            
            flash_data = {
                'unit_id': unit.id,
                'serial_number': unit.serial_number,
                'model': unittype.model,
                'Pmax': moduleproperty.nameplate_pmax,
                'Pmp': result_dict.get("Pmp"),
                'Voc': result_dict.get("Voc"),
                'Vmp': result_dict.get("Vmp"),
                'Isc': result_dict.get("Isc"),
                'Imp': result_dict.get("Imp"),
                'Temperature': result_dict.get("Temperature"),
                'Irradiance': result_dict.get("Irradiance"),
                'V': moduleproperty.voc,
                'Vm': moduleproperty.vmp,
                'Is': moduleproperty.isc,
                'Im': moduleproperty.imp,
            }

            return [{
                'test_name': obj.name,
                'flash_data': [flash_data],
            }]
        else:
            return []
    


    class Meta:
        model = ProcedureResult
        fields = ['id', 'const_rows']


class GetDeliverablesDataImagesSerializer(serializers.ModelSerializer):
    el_images = serializers.SerializerMethodField()

    def get_el_images(self, obj):
        unit = Unit.objects.filter(id=obj.unit_id).first()
        if not unit:
            return None

        # Get all measurement results related to the current ProcedureResult
        measurements = MeasurementResult.objects.filter(step_result__procedure_result=obj.id)

        # Filter measurements to include only 'EL Image (grayscale)'
        filtered_measurements = measurements.filter(name__in=['EL Image (grayscale)'])
        if not filtered_measurements.exists():
            return None

        # Fetch Azure files linked to the filtered measurements
        azure_file_ids = filtered_measurements.values_list('result_files__id', flat=True)
        azure_files = AzureFile.objects.filter(id__in=azure_file_ids)

        # Serialize Azure files
        serializer = AzureFileSerializer(
            azure_files, many=True, context={'request': self.context.get('request')}
        )
        serialized_data = serializer.data

        first_file_url = serialized_data[0]['file'] if serialized_data else None

        # Fetch the procedure definition name
        procedure_definition = ProcedureDefinition.objects.filter(id=obj.procedure_definition_id).first()
        if procedure_definition:
            test_name = procedure_definition.name
        else:
            test_name = None  # Handle case where no ProcedureDefinition is found

        return {
            'serial_number': unit.serial_number,
            'items': [
                {
                    'test_name': test_name,
                    'image_url': first_file_url,
                }
            ],
        }

    class Meta:
        model = ProcedureResult
        fields = ['el_images']
