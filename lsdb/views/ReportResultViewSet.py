from rest_framework import viewsets,status
from lsdb.models import ReportResult,ReportExecutionOrder,WorkOrder,ReportSequenceDefinition,Disposition
from lsdb.serializers import ReportResultSerilaizer,ReportExecutionOrderSerializer,DispositionSerializer
from rest_framework.decorators import action
from django.db import IntegrityError, transaction
from rest_framework.response import Response


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



