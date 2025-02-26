from rest_framework import viewsets
from lsdb.models import DispositionCode, ReportSequenceDefinition,ReportExecutionOrder,ProductTypeDefinition, ReportTypeDefinition
from lsdb.serializers import ReportSequenceDefinitionSerializer,ReportExecutionOrderSerializer
import json
from rest_framework.response import Response
from rest_framework.decorators import action
import json
from django.db import IntegrityError, transaction
from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from lsdb.serializers import MockTravelerSerializer
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.permissions import ConfiguredPermission

class TestSequenceDefinitionFilter(filters.FilterSet):
    class Meta:
        model = ReportSequenceDefinition
        fields = [
            'disposition',
        ]


class ReportSequenceDefinitionViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ReportSequenceDefinition to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ReportSequenceDefinition.objects.all()
    serializer_class = ReportSequenceDefinitionSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)

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
            serializer_class=ReportSequenceDefinitionSerializer,
            )
    def delete_report_procedure(self, request, pk=None):
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
        report_sequence = ReportSequenceDefinition.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for execution in params:

                report_definition = ReportTypeDefinition.objects.get(id=execution.get('report_definition_id'))
                product_definition = ProductTypeDefinition.objects.get(id=execution.get('product_definition_id'))
                ReportExecutionOrder.objects.filter(execution_group_name=execution.get('execution_group_name'),
                                                    report_definition=report_definition,
                                                    product_definition=product_definition,
                                                    execution_group_number=execution.get('execution_group_number'),
                                                    report_sequence_definition=report_sequence).delete()
                
        serializer = ReportSequenceDefinitionSerializer(report_sequence, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get'],
            serializer_class=MockTravelerSerializer,
            )
    def mock_traveler(self, request, pk=None):
        queryset = ReportSequenceDefinition.objects.get(id=pk)
        self.context = {'request': request}
        serializer = self.serializer_class(queryset, many=False, context=self.context)
        # print(serializer.data)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ReportSequenceDefinitionSerializer
            )
    def rsd_full_view(self, request, pk=None):
        queryset = ReportExecutionOrder.objects.filter(report_sequence_definition=pk)
        self.context = {'request': request}
        serializer = ReportExecutionOrderSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ReportSequenceDefinitionSerializer,
            )
    def add_reports(self, request, pk=None):
        """
        This action is used to add report definitions to a report sequence definition. Each link requires a non-unique execution group.
        POST:
        [
        {
        "execution_group_name":"new test",
        "report_definition_id":1,
        "product_definition_id":1,
        "execution_group_number":3,
        "report_sequence_definition_id":1
        }
        ]
        

        This is a destructive process, sending an empty name will delete the name.
        """
        self.context = {'request': request}
        report_sequence = ReportSequenceDefinition.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            print(params)
            for execution in params:

                report_definition = ReportTypeDefinition.objects.get(id=execution.get('report_definition_id'))
                product_definition = ProductTypeDefinition.objects.get(id=execution.get('product_definition_id'))


                ReportExecutionOrder.objects.create(execution_group_name=execution.get('execution_group_name'),
                                                    report_definition=report_definition,
                                                    product_definition=product_definition,
                                                    execution_group_number=execution.get('execution_group_number'),
                                                    report_sequence_definition=report_sequence)
        serializer = ReportSequenceDefinitionSerializer(report_sequence, many=False, context=self.context)
        return Response(serializer.data)
