from rest_framework import viewsets, status
from rest_framework.response import Response
from lsdb.models import ProcedureResult
from lsdb.serializers import GetDeliverablesDataSerializer
from lsdb.serializers.GetDeliverablesDataSerializer import GetDeliverablesDataImagesSerializer
from rest_framework.decorators import action


class GetDeliverablesDataViewSet(viewsets.ModelViewSet):
    queryset = ProcedureResult.objects.all()  
    serializer_class = GetDeliverablesDataSerializer

    @action(detail=False, methods=['post'])
    def deliverables_data(self, request):
        work_order_id = request.data.get("work_order_id")
        procedure_definition_id = request.data.get("procedure_definition_id")

        if not work_order_id or not procedure_definition_id:
            return Response({"error": "work_order_id and procedure_definition_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        procedures = ProcedureResult.objects.filter(work_order_id=work_order_id, procedure_definition_id=procedure_definition_id)

        if not procedures.exists():
            return Response({"error": "No procedures found for the given work_order_id and procedure_definition_id."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GetDeliverablesDataSerializer(procedures,many=True,context={"work_order_id": work_order_id,"procedure_definition_id": procedure_definition_id,"request": request,},)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def el_images(self, request):
        work_order_id = request.data.get("work_order_id")
        test_sequence_id = request.data.get("test_sequence_id")
        if not work_order_id or not test_sequence_id:
            return Response({"error": "work_order_id and test_sequence_id are required."}, status=status.HTTP_400_BAD_REQUEST)
        procedures = ProcedureResult.objects.filter(work_order_id=work_order_id, test_sequence_definition_id=test_sequence_id)
        procedure_definition_id = request.data.get("procedure_definition_id")

        if not work_order_id or not procedure_definition_id:
            return Response({"error": "work_order_id and procedure_definition_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        procedures = ProcedureResult.objects.filter(work_order_id=work_order_id, procedure_definition_id=procedure_definition_id)

        if not procedures.exists():
            return Response({"error": "No procedures found for the given work_order_id and test_sequence_id."}, status=status.HTTP_404_NOT_FOUND)
        serializer = GetDeliverablesDataImagesSerializer(procedures,many=True,context={"work_order_id": work_order_id,"procedure_definition_id": procedure_definition_id,"request": request,},)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
        

        

