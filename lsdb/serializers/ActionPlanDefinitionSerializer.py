from django.db import IntegrityError, transaction
import pandas as pd
from rest_framework import serializers
from lsdb.models import ActionPlanDefinition
from lsdb.models import ActionExecutionOrder

from lsdb.serializers.ActionDefinitionSerializer import ActionDefinitionSerializer


class ActionExecutionOrderSerializer(serializers.ModelSerializer):
    action_definition = ActionDefinitionSerializer(many=False)

    class Meta:
        model = ActionExecutionOrder
        fields = [
            'execution_group_number',
            'execution_group_name',
            'action_plan',
            'action_definition',
        ]

class ActionPlanDefinitionSerializer(serializers.ModelSerializer):
    action_definitions = ActionExecutionOrderSerializer(source='actionexecutionorder_set', many=True, read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name')

    class Meta:
        model = ActionPlanDefinition
        fields = [
            'id',
            'url',
            'name',
            'description',
            'disposition',
            'disposition_name',
            'groups',
            'unit_type_family',
            'action_definitions',
        ]

    # def create(self, validated_data):
    #     action_data = validated_data.pop('actiondefinition_set')
    #     action_definition = ActionPlanDefinition.objects.create(**validated_data)
    #
    #     for action in action_data:
    #         d = dict(action)
    #         ActionExecutionOrder.objects.create(
    #             test_sequence=test_sequence_definition,
    #             action_definition=d['action_definition'],
    #             execution_number=d['execution_number'],
    #             allow_skip=d['allow_skip'],
    #         )
    #
    #     return test_sequence_definition

    # def update(self, instance, validated_data):
    #     action_data = validated_data.pop('actiondefinition_set')
    #
    #     for item in validated_data:
    #         if ActionPlanDefinition._meta.get_field(item):
    #             setattr(instance, item, validated_data[item])
    #
    #     actionExecutionOrder.objects.filter(test_sequence=instance).delete()
    #
    #     for action in action_data:
    #         d = dict(action)
    #         actionExecutionOrder.objects.create(
    #             test_sequence=instance,
    #             action_definition=d['action_definition'],
    #             execution_condition=d['execution_number'],
    #             allow_skip=d['allow_skip']
    #         )
    #
    #     instance.save()
    #     return instance
