from django.db import IntegrityError, transaction
import pandas as pd
from rest_framework import serializers
from lsdb.models import TestSequenceDefinition
from lsdb.models import ProcedureExecutionOrder

from lsdb.serializers.ProcedureDefinitionSerializer import ProcedureDefinitionSerializer


class ProcedureExecutionOrderSerializer(serializers.ModelSerializer):
    procedure_definition = ProcedureDefinitionSerializer(many=False,
         )

    class Meta:
        model = ProcedureExecutionOrder
        fields = [
            'execution_group_name',
            'execution_group_number',
            'execution_condition',
            'allow_skip',
            # 'test_sequence',
            'procedure_definition',
            'execution_condition',
        ]


class StaticField(serializers.Field):
    def to_representation(self,value): return value
    def to_internal_value(self, data): return data


class MockTravelerSerializer(serializers.ModelSerializer):
    customer_name = StaticField("Cypress Ave. Solar Equipment")
    project_manager = StaticField("project.manager@pvel.com")
    project_number = StaticField("THX-1138")
    grouped_results = serializers.SerializerMethodField()
    location = StaticField("LGA")
    # unit_type = UnitTypeSerializer(read_only=True, many=False)
    work_order_name  = StaticField("T-16")
    test_sequence_definition_name = serializers.ReadOnlyField(source='name')
    notes = StaticField([])
    # tib = StaticField(None)
    disposition_name = StaticField("Test Disposition")
    fixture_location = StaticField("N/A")
    crate = StaticField("N/A")
    serial_number = StaticField("N/A")
    location= StaticField("N/A")
    name = StaticField("N/A")
    description = StaticField("N/A")
    notes = StaticField("N/A")
    unit_images = StaticField("N/A")
    unit_type = StaticField("N/A")

    @transaction.atomic
    def get_grouped_results(self, obj):
        queryset = obj.procedureexecutionorder_set.all()

        if not queryset: return []
        master_data_frame = pd.DataFrame(list(queryset.values(
            'id',
            'execution_group_name',
            'execution_group_number',
            'procedure_definition',
            'procedure_definition__name',
            'procedure_definition__visualizer__name',
        )))
        master_data_frame.columns=[
            'id',
            'name',
            'linear_execution_group',
            'procedure_definition',
            'procedure_definition_name',
            'visualizer',
            ]
        master_data_frame['disposition_name'] = None
        master_data_frame['completion_date'] = None
        master_data_frame['username'] = None
        master_data_frame['reviewed_by_user'] = None
        master_data_frame['review_datetime'] = None
        master_data_frame['start_datetime'] = None
        master_data_frame['end_datetime'] = None

        # master_data_frame.completion_date.astype(object).where(master_data_frame.completion_date.notna(),None, inplace=True,)
        grouped = master_data_frame.groupby('linear_execution_group')
        results = []
        for name, group in grouped:
            full = {}
            full["procedure_results"] = group.to_dict(orient='records')
            full["name"] = full["procedure_results"][0]["name"]
            full["linear_execution_group"] = full["procedure_results"][0]["linear_execution_group"]
            for result in full["procedure_results"]:
                for date_string in ['completion_date','review_datetime','start_datetime','end_datetime']:
                    if str(result[date_string]) == "NaT":
                        result[date_string] = None
            results.append(full)

        return (results)

    class Meta:
        model = TestSequenceDefinition
        fields = [
            'project_manager',
            'project_number',
            'customer_name',
            'id',
            'url',
            # 'tib',
            'disposition_name',
            'test_sequence_definition_name',
            'work_order_name',
            'fixture_location',
            'crate',
            'serial_number',
            'location',
            'name',
            'description',
            'notes',
            'unit_images',
            'unit_type',
            'hex_color',
            'grouped_results',
        ]


class TestSequenceDefinitionSerializer(serializers.ModelSerializer):
    disposition_name = serializers.ReadOnlyField(source='disposition.name')

    class Meta:
        model = TestSequenceDefinition
        fields = [
            'id',
            'url',
            'name',
            'short_name',
            'description',
            'notes',
            'disposition',
            'disposition_name',
            'version',
            'group',
            'unit_type_family',
            'hex_color',
        ]


class TestSequenceDefinitionSerializerFull(serializers.ModelSerializer):
    procedure_definitions = ProcedureExecutionOrderSerializer(source='procedureexecutionorder_set', many=True, read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name')

    class Meta:
        model = TestSequenceDefinition
        fields = [
            'id',
            'url',
            'name',
            'short_name',
            'description',
            'notes',
            'disposition',
            'disposition_name',
            'version',
            'group',
            'unit_type_family',
            'procedure_definitions',
            'hex_color',
        ]

    def create(self, validated_data):
        procedure_data = validated_data.pop('proceduredefinition_set')
        test_sequence_definition = TestSequenceDefinition.objects.create(**validated_data)

        for procedure in procedure_data:
            d = dict(procedure)
            ProcedureExecutionOrder.objects.create(
                test_sequence=test_sequence_definition,
                procedure_definition=d['procedure_definition'],
                execution_number=d['execution_number'],
                allow_skip=d['allow_skip'],
            )

        return test_sequence_definition

    def update(self, instance, validated_data):
        procedure_data = validated_data.pop('proceduredefinition_set')

        for item in validated_data:
            if TestSequenceDefinition._meta.get_field(item):
                setattr(instance, item, validated_data[item])

        ProcedureExecutionOrder.objects.filter(test_sequence=instance).delete()

        for procedure in procedure_data:
            d = dict(procedure)
            ProcedureExecutionOrder.objects.create(
                test_sequence=instance,
                procedure_definition=d['procedure_definition'],
                execution_condition=d['execution_number'],
                allow_skip=d['allow_skip']
            )

        instance.save()
        return instance


'''
{
    "name": "test test sequence definition",
    "description": "",
    "notes": "",
    "disposition": 1,
    "version": "0.1",
    "group": 1,
    "unit_type_family": 1,
    "procedure_definitions": [
        {"procedure_definition":1, "execution_number":1, "allow_skip":true },
        {"procedure_definition":2, "execution_number":2, "allow_skip":true }
    ]
}
'''
