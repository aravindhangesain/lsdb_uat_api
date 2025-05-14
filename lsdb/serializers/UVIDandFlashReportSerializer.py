from rest_framework import serializers
from lsdb.models import StepResult, UnitType
from lsdb.models import MeasurementResult
from lsdb.models import ProcedureResult
from lsdb.models import Unit

class UVIDandFlashReportSerializer(serializers.HyperlinkedModelSerializer):
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    unit_serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    disposition_name = serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    flash_start_datetime = serializers.SerializerMethodField()
    module_type_name = serializers.SerializerMethodField()
    date_time=serializers.SerializerMethodField()
    flash_values = serializers.SerializerMethodField()

    def get_flash_values(self, obj):
        stepresult_id = StepResult.objects.filter(procedure_result_id=obj.id).values_list('id', flat=True).first()
        measurementresults = MeasurementResult.objects.filter(step_result_id=stepresult_id,name__in=["Imp", "Isc", "Vmp", "Voc", "Pmp","Temperature", "Irradiance"])
        correction_factor = {}
        for measurementresult in measurementresults:
            if measurementresult.name is not None:
                if measurementresult.result_double is not None:
                    correction_factor[measurementresult.name] = round(measurementresult.result_double, 2)
                else:
                    correction_factor[measurementresult.name] = None
        return correction_factor

    def get_flash_start_datetime(self, obj):
        step_results = StepResult.objects.filter(procedure_result_id=obj)
        measurement_result = MeasurementResult.objects.filter(step_result_id__in=step_results,start_datetime__isnull=False).first()
        if measurement_result:
            return measurement_result.start_datetime
        return None
    
    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None
        
    def get_module_type_name(self, obj):
        unit = Unit.objects.filter(id=obj.unit_id).first()
        if unit:
            unittype = unit.unit_type_id
            name = UnitType.objects.filter(id=unittype).values_list('model',flat=True).first()
            return name
        else:
            return None
        
    def get_date_time(self,obj):
        stepresult_id=StepResult.objects.filter(procedure_result_id=obj.id).values_list('id',flat=True).first()
        date_time=MeasurementResult.objects.filter(step_result_id=stepresult_id).values_list('date_time',flat=True).first()
        return date_time
        

    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'name',
            'unit',
            'unit_id',
            'unit_serial_number',
            'procedure_definition',
            'procedure_definition_name',
            'disposition',
            'disposition_name',
            'start_datetime',
            'project_number',
            'work_order',
            'work_order_name',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'customer_name',
            'flash_start_datetime',
            'module_type_name',
            'date_time',
            'flash_values',
        ]