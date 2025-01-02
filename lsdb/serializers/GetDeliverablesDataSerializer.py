from rest_framework import serializers
from lsdb.models import ProcedureResult, Unit, UnitType, ModuleProperty, MeasurementResult


class GetDeliverablesDataSerializer(serializers.ModelSerializer):
    const_rows = serializers.SerializerMethodField()

    def get_const_rows(self, obj):
        work_order_id = self.context.get("work_order_id")
        test_sequence_id = self.context.get("test_sequence_id")

        if not work_order_id or not test_sequence_id:
            return []  
        
        procedures = ProcedureResult.objects.filter(work_order_id=work_order_id, test_sequence_definition_id=test_sequence_id)

        deliverable_datas = []

        for procedure in procedures:
            unit = Unit.objects.filter(id=procedure.unit_id).first()
            if not unit:
                continue

            unittype = UnitType.objects.filter(id=unit.unit_type_id).first()
            if not unittype:
                continue

            moduleproperty = ModuleProperty.objects.filter(id=unittype.id).first()
            if not moduleproperty:
                continue

            measurements = MeasurementResult.objects.filter(step_result__procedure_result=procedure.id)
            result_dict = {measurement.name: measurement.result_double for measurement in measurements}

            flash_data = {
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

            deliverable_datas.append({
                'test_name': procedure.name,
                'flash_data': [flash_data],
            })

        return deliverable_datas

    class Meta:
        model = ProcedureResult
        fields = ['id', 'const_rows']
