from rest_framework import serializers
from lsdb.models import *
import random
from lsdb.serializers import *
from django.db.models import Max, Min, Q
from django.db.models.functions import Coalesce

class NewFlashTestSerializer(serializers.ModelSerializer):
    # procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    # serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    module_property = serializers.SerializerMethodField()
    unit_type = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    project_number = serializers.SerializerMethodField()
    bom = serializers.SerializerMethodField()
    # filename = serializers.SerializerMethodField()
    # test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')

    def get_project_number(self, obj):
        unit = obj
        if not unit:
            return None
        project = unit.project_set.first()
        if not project:
            return None
        return project.number
    
    def get_customer_name(self, obj):
        unit = obj
        if not unit:
            return None
        project = unit.project_set.first()
        if not project:
            return None
        customer = project.customer
        if not customer:
            return None
        return customer.name
    
    def get_bom(self, obj):
        unit = obj
        if not unit:
            return None
        workorder = unit.workorder_set.first()
        if not workorder:
            return None
        return workorder.name

    def get_unit_type(self, obj):
        unit_type_id = Unit.objects.filter(id=obj.id).values_list('unit_type_id', flat=True).first()
        if unit_type_id:
            unit_type = UnitType.objects.get(id=unit_type_id)
            full_data = UnitTypeSerializer(unit_type, context=self.context).data
            required_fields = ['model', 'manufacturer_name', 'unit_type_family_name']
            filtered_data = {key: full_data[key] for key in required_fields}
            return filtered_data
        return None

    def get_module_property(self, obj):
        unit_type_id = Unit.objects.filter(id=obj.id).values_list('unit_type_id', flat=True).first()
        module_property_id = UnitType.objects.filter(id=unit_type_id).values_list('module_property_id', flat=True).first()
        if not module_property_id:
            return None
        module_property = ModuleProperty.objects.get(id=module_property_id)
        desired_fields = [
            'id', 'number_of_cells', 'nameplate_pmax',
            'module_width', 'module_height', 'system_voltage',
            'module_technology_name', 'isc', 'voc', 'imp', 'vmp',
            'alpha_isc', 'beta_voc', 'gamma_pmp',
            'cells_in_series', 'cells_in_parallel',
            'cell_area', 'bifacial'
        ]
        module_property_serializer = ModulePropertySerializer(module_property, context=self.context)
        full_data = module_property_serializer.data
        filtered_data = {
            field: full_data.get(field)
            for field in desired_fields
        }
        flash_defaults = {
            'alpha_stc_correction_A_per_C': None,
            'beta_stc_correction_V_per_C': None,
            'kappa_stc_correction_Ohm_per_C': None,
            'R_s_stc_correction_Ohm': None,
            'flash_parameters': None,
        }
        filtered_data.update(flash_defaults)
        new_flashtest_points = NewFlashTestPoints.objects.filter(unit_type_id=unit_type_id).values(
            'alpha_stc_correction_A_per_C',
            'beta_stc_correction_V_per_C',
            'kappa_stc_correction_Ohm_per_C',
            'R_s_stc_correction_Ohm',
            'flash_parameters'
        ).order_by('-id').first()
        if new_flashtest_points:
            filtered_data.update(new_flashtest_points)
        flash_data=self.flash(serial_number=obj.serial_number)
        if flash_data:
            filtered_data.update({
                'procedure_result_id': flash_data.get('id'),
                'linear_exec_grp_number': flash_data.get('linear_exec_grp_number'),
                'procedure_definition_name': flash_data.get('procedure_definition'),
            })
        else:
            filtered_data.update({
                'flash_procedure_id': None,
                'flash_linear_exec_grp_number': None,
                'flash_procedure_definition': None,
            })
        return filtered_data
    
    def flash(self,serial_number=None):
        serial_number = serial_number
        units = Unit.objects.filter(serial_number=serial_number)
        unit = units.first()
        if not unit:
            return None
        try:
            procedure_definitions = [14, 54, 50, 62, 33, 49, 21, 38, 48]
            procedure_results = unit.procedureresult_set.filter(
                Q(disposition__isnull=True) | Q(disposition__complete=False) 
            ).exclude(supersede=True).filter(procedure_definition__id__in=procedure_definitions)
            done_to = unit.procedureresult_set.aggregate(
                done_to=Coalesce(
                    Max(
                        "linear_execution_group",
                        filter=Q(
                            disposition__isnull=False,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede__isnull=True,
                        )
                        | Q(
                            disposition__isnull=False,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede=False,
                        ),
                    ),
                    0.0,
                )
            ).get("done_to")
            previous_group = unit.procedureresult_set.filter(
                linear_execution_group=done_to,
                test_sequence_definition__group__name__iexact="sequences",
            ).filter(disposition_id=7)
            if previous_group.exists():
                group = previous_group.last()
                group_name = group.name if hasattr(group, "name") else group.linear_execution_group
                return None
            if done_to != 0.0:
                procedure_results = procedure_results.exclude(
                    linear_execution_group__lt=done_to,
                    test_sequence_definition__group__name__iexact="sequences",
                )
            highest_leg = unit.procedureresult_set.aggregate(
                highest_leg=Coalesce(
                    Min(
                        "linear_execution_group",
                        filter=Q(
                            disposition__isnull=True,
                            linear_execution_group__gt=done_to,
                            allow_skip=False,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede__isnull=True,
                        )
                        | Q(
                            disposition__isnull=True,
                            allow_skip=False,
                            linear_execution_group__gt=done_to,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede=False,
                        ),
                    ),
                    99.0,
                )
            ).get("highest_leg")
            procedure_results = procedure_results.exclude(
                linear_execution_group__gt=highest_leg,
                test_sequence_definition__group__name__iexact="sequences",
            ).values_list('id',flat=True)
            procedure_results = list(procedure_results)
            if procedure_results is None:
                None
            procedure=ProcedureResult.objects.filter(id__in=procedure_results).first()
            current_procedure={
                'id':procedure.id,
                'linear_exec_grp_number':procedure.linear_execution_group,
                'procedure_definition':procedure.procedure_definition.name
            }
            return current_procedure
        except Exception as e:
            None

    # def get_filename(self, obj):
    #     test_generated_number = random.randint(10000, 99999)
    #     serial_number = Unit.objects.filter(id=obj.unit.id).values_list('serial_number', flat=True).first()
    #     unit_type_id = Unit.objects.filter(id=obj.unit.id).values_list('unit_type_id', flat=True).first()
    #     module_property_id = UnitType.objects.filter(id=unit_type_id).values_list('module_property_id', flat=True).first()
    #     isc = ModuleProperty.objects.filter(id=module_property_id).values_list('isc', flat=True).first()
    #     if isc is not None:
    #         isc_str = str(isc)
    #         if '.' in isc_str:
    #             isc = isc_str.replace('.', '_') 
    #     return f"DSC_{test_generated_number}_{serial_number}_{isc}A_1s"
    
    class Meta:
        model = Unit
        fields = [
            # 'id',
            # 'unit',
            # 'serial_number',
            # 'test_sequence_definition',
            # 'test_sequence_definition_name',
            'module_property',
            'unit_type',
            'project_number',
            'customer_name',
            'bom',
            # 'filename',
            # 'name',
            # 'procedure_definition',
            # 'procedure_definition_name',
            # 'disposition'
        ]
