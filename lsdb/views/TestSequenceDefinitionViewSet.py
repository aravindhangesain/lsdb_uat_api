import json
from django.db import IntegrityError, transaction
from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.models import DispositionCode
from lsdb.models import ProcedureDefinition
from lsdb.models import TestSequenceDefinition
from lsdb.models import ProcedureExecutionOrder
from lsdb.serializers import TestSequenceDefinitionSerializer
from lsdb.serializers import MockTravelerSerializer
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.permissions import ConfiguredPermission
from lsdb.serializers.TestSequenceDefinitionSerializer import TestSequenceDefinitionSerializerFull


class TestSequenceDefinitionFilter(filters.FilterSet):
    class Meta:
        model = TestSequenceDefinition
        fields = [
            'disposition',
        ]


class TestSequenceDefinitionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows TestSequenceDefinition to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = TestSequenceDefinition.objects.all()
    serializer_class = TestSequenceDefinitionSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TestSequenceDefinitionFilter

    @action(detail=False, methods=['get', ],
            serializer_class=DispositionCodeListSerializer,
            )
    def dispositions(self, request, pk=None):
        self.context = {'request': request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='test_sequence_definitions'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=TestSequenceDefinitionSerializer,
            )
    def delete_procedures(self, request, pk=None):
        """
        This action is used to remove procedure definitions from a test sequence definition. The link is located via perfect matches to test_sequence,
        POST:
        [
            {
                "execution_group_name": "TC800 pre flash",
                "execution_group_number": 1,
                "procedure_definition": 1
            },
            ...
        ]
        "execution_group_name": name of procedure to delete,
        "execution_group_number": grouping of procedures to isolate this procedurer,
        "procedure_definition": ID of the procedure to delete

        """
        self.context = {'request': request}
        test_sequence = TestSequenceDefinition.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for procedure in params:
                procedure_definition = ProcedureDefinition.objects.get(id=procedure.get('procedure_definition'))

                ProcedureExecutionOrder.objects.filter(
                    execution_group_name=procedure.get('execution_group_name'),
                    execution_group_number=procedure.get('execution_group_number'),
                    procedure_definition=procedure_definition,
                    test_sequence=test_sequence,
                ).delete()

        serializer = TestSequenceDefinitionSerializer(test_sequence, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get'],
            serializer_class=MockTravelerSerializer,
            )
    def mock_traveler(self, request, pk=None):
        queryset = TestSequenceDefinition.objects.get(id=pk)
        self.context = {'request': request}
        serializer = self.serializer_class(queryset, many=False, context=self.context)
        # print(serializer.data)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=TestSequenceDefinitionSerializerFull
            )
    def tsd_full_view(self, request, pk=None):
        queryset = TestSequenceDefinition.objects.get(id=pk)
        self.context = {'request': request}
        serializer = self.serializer_class(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=TestSequenceDefinitionSerializer,
            )
    def add_procedures(self, request, pk=None):
        """
        This action is used to add procedure definitions to a test sequence definition. Each link requires a non-unique execution group for ordering, and an allow_skip setting.
        POST:
        [
            {
                "execution_group_name": "TC800 pre flash",
                "execution_group_number": 1,
                "allow_skip": true,
                "procedure_definition": 1,
                "execution_condition":"unit.unit_type.module_property.bifacial"
            },
            ...
        ]
        "execution_group_name": optional name for displaying this procedure in this test sequence,
        "execution_group_number": grouping of procedures to enforce an order,
        "allow_skip": tells server if this procedure must be completed before the next execution group can be started,
        "procedure_definition": ID of the procedure to link
        "execution_condition": Optional string that will be run through exec() to determine if this procedure should be added.

        This is a destructive process, sending an empty name will delete the name.
        """
        self.context = {'request': request}
        test_sequence = TestSequenceDefinition.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for procedure in params:
                procedure_definition = ProcedureDefinition.objects.get(id=procedure.get('procedure_definition'))
                # TODO: Better exception handling here
                procedure_link = ProcedureExecutionOrder.objects.create(
                    execution_group_name=procedure.get('execution_group_name'),
                    execution_group_number=procedure.get('execution_group_number'),
                    allow_skip=procedure.get('allow_skip'),
                    procedure_definition=procedure_definition,
                    test_sequence=test_sequence,
                    execution_condition=procedure.get('execution_condition'),
                )
        serializer = TestSequenceDefinitionSerializer(test_sequence, many=False, context=self.context)
        return Response(serializer.data)
