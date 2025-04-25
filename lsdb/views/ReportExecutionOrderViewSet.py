from rest_framework import viewsets,status
from lsdb.models import ReportExecutionOrder,TestSequenceDefinition,ProcedureExecutionOrder,ProcedureDefinition
from lsdb.serializers import ReportExecutionOrderSerializer, TestSequenceDefinitionSerializer,ProcedureDefinitionSerializer
from rest_framework.decorators import action
from django.db import IntegrityError, transaction
from rest_framework.response import Response




class ReportExecutionOrderViewSet(viewsets.ModelViewSet):
    queryset = ReportExecutionOrder.objects.all()
    serializer_class = ReportExecutionOrderSerializer

    @transaction.atomic
    @action(detail=True, methods=['get', 'patch'],)
    def update_report_execution_order(self, request, pk=None):

        
        data=request.data.copy()

        report_execution_order = self.get_object()
        serializer = ReportExecutionOrderSerializer(report_execution_order, data=data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Report Execution Order updated successfully",
                "updated_response": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['get'])
    def available_tsd(self, request):

        available_tests=TestSequenceDefinition.objects.filter(disposition_id=16)
        serializer=TestSequenceDefinitionSerializer(available_tests, many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post','get'])
    def selected_tsd(self, request):
        selected_test_sequence_id = request.data.get('test_sequence_id')
        procedure_ids=ProcedureExecutionOrder.objects.filter(test_sequence_id=selected_test_sequence_id).values_list('procedure_definition_id', flat=True)

        procedures = ProcedureDefinition.objects.filter(id__in=procedure_ids)
        serializer=ProcedureDefinitionSerializer(procedures, many=True,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


            

        

        


       

        
    


    