from rest_framework import viewsets,status
from lsdb.models import ReportExecutionOrder
from lsdb.serializers import ReportExecutionOrderSerializer
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


    