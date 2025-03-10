import json
from django.db import IntegrityError, transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from django_filters import rest_framework as filters

from lsdb.serializers import ProcedureDefinitionSerializer
from lsdb.models import ProcedureDefinition
from lsdb.models import StepDefinition
from lsdb.models import StepExecutionOrder
from lsdb.permissions import ConfiguredPermission

class ProcedureDefinitionFilter(filters.FilterSet):

    class Meta:
        model = ProcedureDefinition
        fields = {
            'version':['exact','icontains'],
            'name':['exact','icontains'],
            'disposition': ['exact']
        }

class ProcedureDefinitionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ProcedureDefinition to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ProcedureDefinition.objects.all()
    serializer_class = ProcedureDefinitionSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProcedureDefinitionFilter

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class = ProcedureDefinitionSerializer,
    )
    def delete_steps(self, request, pk=None):
        """
        This action is used to remove procedure definitions from a test sequence definition. The link is located via perfect matches to test_sequence,
        POST:
        [
            {
                "execution_group_number": 1,
                "step_definition": 1
            },
            ...
        ]
        "execution_group_number": step number to isolate record to delete,
        "step_definition": ID of the procedure to unlink
        """
        self.context = {'request':request}
        procedure = ProcedureDefinition.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for step in params:
                step_definition = StepDefinition.objects.get(id=step.get('step_definition'))

                StepExecutionOrder.objects.filter(
                    execution_group_number = step.get('execution_group_number'),
                    procedure_definition = procedure,
                    step_definition = step_definition,
                ).delete()

        serializer = ProcedureDefinitionSerializer(procedure,many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class = ProcedureDefinitionSerializer,
    )
    def add_steps(self, request, pk=None):
        """
        This action is used to add step definitions to a preocedure definition. Each link requires a non-unique execution group for ordering, and an allow_skip setting.
        POST:
        [
            {
                "execution_group_number": 1,
                "execution_group_name":  "I-V curve at 25 °C, 1000 W/m²",
                "allow_skip": true,
                "step_definition": 1
            },
            ...
        ]
        "execution_group_number": grouping of procedures to enforce an order,
        "allow_skip": tells server if this procedure must be completed before the next execution group can be started,
        "step_definition": ID of the procedure to link
        """
        self.context = {'request': request}
        procedure = ProcedureDefinition.objects.get(id=pk)

        if request.method == "POST":
            params = json.loads(request.body)
            
            # Pre-fetch special StepDefinition instances
            special_steps = {
                "Test Start": StepDefinition.objects.get(id=6),
                "Test Pause": StepDefinition.objects.get(id=31),
                "Test Resume": StepDefinition.objects.get(id=32),
                "Test End": StepDefinition.objects.get(id=5),
            }

            for step in params:
                step_definition = StepDefinition.objects.get(id=step.get('step_definition'))

                if not StepExecutionOrder.objects.filter(procedure_definition=procedure, step_definition=step_definition).exists():
                    # Check if the step is a special test step
                    if step_definition.name in special_steps:
                        # Create all special test steps
                        for step_name, step_instance in special_steps.items():
                            StepExecutionOrder.objects.create(
                                execution_group_name=step_name,
                                execution_group_number={
                                    "Test Start": 1,
                                    "Test End": 2,
                                    "Test Pause": 3,
                                    "Test Resume": 4,
                                }[step_name],
                                allow_skip=step.get('allow_skip'),
                                procedure_definition=procedure,
                                step_definition=step_instance,
                            )
                    else:
                        # Create a regular step execution order
                        StepExecutionOrder.objects.create(
                            execution_group_name=step.get('execution_group_name'),
                            execution_group_number=step.get('execution_group_number'),
                            allow_skip=step.get('allow_skip'),
                            procedure_definition=procedure,
                            step_definition=step_definition,
                        )

        serializer = ProcedureDefinitionSerializer(procedure, many=False, context=self.context)
        return Response(serializer.data)
'''
[
{                "execution_group_number": 1,
                "allow_skip": true,
                "step_definition": 3},
{                "execution_group_number": 2,
                "allow_skip": true,
                "step_definition": 2},
{                "execution_group_number": 3,
                "allow_skip": true,
                "step_definition": 1}
]
'''
