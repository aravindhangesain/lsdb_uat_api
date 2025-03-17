from rest_framework import viewsets,status
from datetime import datetime as dt  

from lsdb.models import ReportResult,ReportExecutionOrder,WorkOrder,ReportSequenceDefinition,Disposition,OpsQueuePriority,ProcedureResult,Unit,TestSequenceDefinition
from lsdb.serializers import ReportResultSerilaizer,ReportExecutionOrderSerializer,DispositionSerializer
from rest_framework.decorators import action
from django.db import IntegrityError, transaction
from rest_framework.response import Response
from django.db import connection


class ReportResultViewSet(viewsets.ModelViewSet):
    # queryset = ReportResult.objects.all()
    serializer_class = ReportResultSerilaizer

    def get_queryset(self):
        """
        Override get_queryset to filter results based on work_order_id.
        """
        queryset = ReportResult.objects.all()
        work_order_id = self.request.query_params.get('work_order_id')

        if work_order_id:
            queryset = queryset.filter(work_order_id=work_order_id)

        return queryset


    @transaction.atomic
    @action(detail=False,serializer_class=ReportResultSerilaizer,methods=['post','get'],)
    def create_report_result(self, request):
        work_order_id=request.data.get('work_order_id')
        report_sequence_definition_id=request.data.get('report_sequence_definition_id')
        
        if ReportResult.objects.filter(work_order_id=work_order_id).exists():
                return Response({"message":"Report already assigned for the given work-order"}, status=status.HTTP_404_NOT_FOUND)
        
        report_results=ReportExecutionOrder.objects.filter(report_sequence_definition_id=report_sequence_definition_id).order_by('execution_group_number')

        for result in report_results:
            workorder=WorkOrder.objects.get(id=work_order_id)
            report_definition=ReportSequenceDefinition.objects.get(id=report_sequence_definition_id)
            
                
            
            ReportResult.objects.create(work_order=workorder,report_sequence_definition=report_definition,
                                            report_execution_order_number=result.execution_group_number,
                                            product_type_definition=result.product_definition,
                                            report_type_definition=result.report_definition,data_ready_status='Define'
                                        )
        
        queryset = ReportResult.objects.all()
        serializer = ReportResultSerilaizer(queryset,many=True, context={'request': request})
        return Response(serializer.data)
    
    @transaction.atomic
    @action(detail=False,methods=["patch","get"], url_path="update_report_result")
    def update_report_result(self, request):
        
        report_result_id=request.data.get('report_result_id')
        if report_result_id:
            try:
                report_result = ReportResult.objects.get(id=report_result_id)
            except ReportResult.DoesNotExist:
                return Response({"message": "ReportResult not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = ReportResultSerilaizer(report_result, data=request.data, partial=True, context={"request": request})

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "ReportResult updated successfully", "updated_response": serializer.data}, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "ReportResult id not provided"}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=False,methods=["get"])
    def report_dispositions(self, request):

        dispositions=Disposition.objects.filter(id__in=[7,20,61,62])
        serializer=DispositionSerializer(dispositions,many=True,context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False,methods=["post","get"])
    def get_unit_tsds(self, request):
        work_order_id = request.query_params.get('work_order_id')

        if not work_order_id:
            return Response({"error": "work_order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT unit_id 
                FROM lsdb_workorder_units 
                WHERE workorder_id = %s
            """, [work_order_id])
            unit_ids = [row[0] for row in cursor.fetchall()]
            if not unit_ids:
                return Response({"No Unit Mapped with this work-order"},status=status.HTTP_200_OK)
            
            unit_tsd_list = []
            if unit_ids:
                for unit_id in unit_ids:
                    test_sequence_definition_id = ProcedureResult.objects.filter(unit_id=unit_id).values_list('test_sequence_definition_id', flat=True).first()

                    serial_number=Unit.objects.filter(id=unit_id).values_list('serial_number',flat=True).first()
                    test_sequence_definition_name=TestSequenceDefinition.objects.filter(id=test_sequence_definition_id).values_list('name',flat=True).first()

                    unit_tsd_list.append({
                        "unit_id": unit_id,
                        "serial_number":serial_number,
                        "test_sequence_definition_id": test_sequence_definition_id,
                        "test_sequence_definition_name":test_sequence_definition_name
                       
                    })

                return Response(unit_tsd_list, status=status.HTTP_200_OK)
    
    # @action(detail=False,methods=["post","get"])
    # def get_unit_procedureresult_name(self, request):

    #     serial_number = request.query_params.get('serial_number')

    #     if serial_number:




            
                

        
