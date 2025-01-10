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
        procedure_definition_ids = request.data.get("procedure_definition_id")

        # Ensure procedure_definition_ids is a list
        if isinstance(procedure_definition_ids, str):
            procedure_definition_ids = procedure_definition_ids.split(",")

        if not work_order_id or not procedure_definition_ids:
            return Response(
                {"error": "work_order_id and procedure_definition_id are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Query ProcedureResult based on work_order_id and procedure_definition_ids
        procedures = ProcedureResult.objects.filter(
            work_order_id=work_order_id,
            procedure_definition_id__in=procedure_definition_ids
        )

        if not procedures.exists():
            return Response(
                {"error": "No procedures found for the given work_order_id and procedure_definition_id."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Group items by serial number
        grouped_data = {}
        for procedure in procedures:
            serializer = GetDeliverablesDataImagesSerializer(procedure, context={"request": request})
            procedure_data = serializer.data.get('el_images')

            if not procedure_data:
                continue

            serial_number = procedure_data['serial_number']
            if serial_number not in grouped_data:
                grouped_data[serial_number] = []

            grouped_data[serial_number].extend(procedure_data['items'])

        # Format response as a list of dictionaries for JSON response
        formatted_response = [
            {"serial_number": serial_number, "items": items}
            for serial_number, items in grouped_data.items()
        ]

        return Response(formatted_response, status=status.HTTP_200_OK)