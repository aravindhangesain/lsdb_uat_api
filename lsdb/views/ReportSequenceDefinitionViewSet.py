from rest_framework import viewsets,status
from lsdb.models import AzureFile, DispositionCode, ReportSequenceDefinition,ReportExecutionOrder,ProductTypeDefinition, ReportTypeDefinition, TestSequenceDefinition
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
            name='report_sequence_definitions'),
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
        instance = self.get_object()
        serialized_data = self.get_serializer(instance, context={'request': request}).data

        # Fetch related ReportExecutionOrder records
        report_execution_orders = ReportExecutionOrder.objects.filter(report_sequence_definition=pk)
        report_execution_orders_data = ReportExecutionOrderSerializer(report_execution_orders, many=True, context={'request': request}).data

        # Constructing the final response structure
        transformed_data = {
            "id": serialized_data["id"],
            "name": serialized_data["name"],
            "short_name": serialized_data["short_name"],
            "description": serialized_data["description"],
            "disposition": serialized_data["disposition"],
            "version": serialized_data["version"],
            "hex_color": serialized_data.get("hex_color", "#FFFFFF"),  # Default to white if not available
            "report_execution_orders": report_execution_orders_data  # Using full serialized data instead of just IDs
        }

        return Response(transformed_data)
    
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
                test_definition=TestSequenceDefinition.objects.get(id=execution.get('test_definition_id'))
                azure_id = execution.get('azure_file_id')
                if azure_id:
                    azure_instance=AzureFile.objects.get(id=azure_id)
                else:
                    azure_instance=None

                ReportExecutionOrder.objects.create(execution_group_name=execution.get('execution_group_name'),
                                                    report_definition=report_definition,
                                                    product_definition=product_definition,
                                                    execution_group_number=execution.get('execution_group_number'),
                                                    test_definition_id=test_definition,
                                                    report_sequence_definition=report_sequence,azure_file=azure_instance,data_ready_status=execution.get('data_ready_status',None))
        serializer = ReportSequenceDefinitionSerializer(report_sequence, many=False, context=self.context)
        return Response(serializer.data)
    
    


        
