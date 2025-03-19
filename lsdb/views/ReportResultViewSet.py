from rest_framework import viewsets,status
from datetime import datetime as dt  

from lsdb.models import ReportResult,ReportExecutionOrder,WorkOrder,ReportSequenceDefinition,Disposition,OpsQueuePriority,ProcedureResult,Unit,TestSequenceDefinition,UnitReportResult
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
        queryset = ReportResult.objects.all().order_by('id')
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
        data_ready_status=request.data.get('data_ready_status')
        execution_number=request.data.get('execution_number')
        work_order_id=request.data.get('work_order_id')

        if report_result_id:
            try:
                report_result = ReportResult.objects.get(id=report_result_id)
            except ReportResult.DoesNotExist:
                return Response({"message": "ReportResult not found"}, status=status.HTTP_404_NOT_FOUND)
            
            is_procedure=request.data.get('is_procedure')

            if is_procedure is False:
                data=request.data.copy()
                patch_data = {
                    "report_result_id":report_result_id,
                    "data_ready_status":data_ready_status,
                    "work_order_id":work_order_id,
                    "is_procedure":data.pop('is_procedure',None)
                }
                serializer = ReportResultSerilaizer(report_result, data=data, partial=True, context={"request": request})


            
            if is_procedure is True:
                data = request.data.copy()
                patch_data = {
                                "execution_number":execution_number,
                                "data_ready_status":data_ready_status,
                                "report_result_id":report_result_id,
                                "serial_number": data.pop('serial_number', None),
                                "is_procedure": data.pop('is_procedure', None)
                            }
            
                serial_number=patch_data.get('serial_number')
                procedureresult_name=patch_data.get('data_ready_status')
                execution_number=patch_data.get('execution_number')
    
                unit_id=Unit.objects.filter(serial_number=serial_number).values_list('id',flat=True).first()
                UnitReportResult.objects.create(procedureresult_name=procedureresult_name,report_result_id=report_result_id,unit_id=unit_id,execution_group_number=execution_number)

                
                serializer = ReportResultSerilaizer(report_result, data=data, partial=True, context={"request": request})
            else:
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
    
    @action(detail=False,methods=["post","get"])
    def get_unit_procedureresult_name(self, request):

        serial_number = request.query_params.get('serial_number')
        unit= Unit.objects.filter(serial_number=serial_number).first()
        proceduresults=[]
        if serial_number:
            procedures=ProcedureResult.objects.filter(unit_id=unit.id).order_by('name', 'id').distinct('name')
            if procedures:
                for procedure in procedures:
                    proceduresults.append({
                        "procedure_execution_order":procedure.linear_execution_group,
                        "name":procedure.name
                    })
                return Response(proceduresults,status=status.HTTP_200_OK)
            else:
                return Response({"No procedures for this unit"},status=status.HTTP_200_OK)
        else:
            return Response({"serial number is required"},status=status.HTTP_200_OK)






            
                

        
