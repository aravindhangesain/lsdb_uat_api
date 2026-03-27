
from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated



class NewFlashTestViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = NewFlashTestSerializer
    permission_classes = [IsAuthenticated]          

    @action(detail=False, methods=['get','post'])
    def flash(self, request):
        if request.method=='POST':
            serial_number = request.data.get("serial_number")
            try:
                units = Unit.objects.get(serial_number=serial_number)
            except Unit.DoesNotExist:
                return Response("Serial Number not found", status=404)
            serializer = NewFlashTestSerializer(units, context={"request": request})
            return Response({"status": "success", "data": [serializer.data]})
        return Response("Enter Payload", status=404)
    
    @action(detail=False, methods=['get','post'])
    def summary_raw(self, request):
        if request.method=='POST':
            choice=request.data.get('choice')
            procedure_result_id = request.data.get('procedure_result_id')
            if choice=='a':
                azure_file_ids = AzureFile.objects.filter(
                    measurementresult__step_result__procedure_result_id=procedure_result_id,
                    measurementresult__name='Data File').values_list('id', flat=True).distinct()
                files = [
                    f"https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/{id}/download/"
                    for id in azure_file_ids]
                return Response({"data": files})
            
            elif choice=='b':
                flash_measurements = MeasurementResult.objects.filter(
                step_result__procedure_result_id=procedure_result_id,
                measurement_result_type__name__icontains='result_double')
                flash = {}
                for measurement in flash_measurements:
                    flash[measurement.name] = measurement.result_double
                return Response ({"data":flash})
        return Response("Enter Payload", status=404)
            





    
    

    # ALLOWED_USERS = {
    #     "IAMTestUser": "xxxxx"
    # }

    # @action(detail=False, methods=['post'])
    # def flash(self, request):
    #     serial_number = request.data.get("serial_number")
    #     username = request.data.get("username")
    #     password = request.data.get("password")
    #     if not username or not password:
    #         return Response({"error": "username and password are required"}, status=400)
    #     allowed_password = self.ALLOWED_USERS.get(username)
    #     if allowed_password != password:
    #         return Response({"error": "Invalid username or password"}, status=403)
    #     try:
    #         unit = Unit.objects.get(serial_number=serial_number)
    #     except Unit.DoesNotExist:
    #         return Response({"error": "Serial Number not found"}, status=404)
    #     serializer = NewFlashTestSerializer(unit, context={"request": request})
    #     return Response({"status": "success", "data": [serializer.data]})
    
    # @action(detail=False, methods=['post'])
    # def flash(self, request):
    #     serial_number = request.data.get("serial_number")
    #     print("Serial Number:", serial_number)
    #     unit = Unit.objects.get(serial_number=serial_number)
    #     if not unit:
    #         return Response("No unit found for the given serial number.", status=404)
    #     try:
    #         procedure_definitions = [14, 54, 50, 62, 33, 49, 21, 38, 48]
    #         procedure_results = unit.procedureresult_set.filter(
    #             procedure_definition__id__in=procedure_definitions
    #         )
    #         if not procedure_results.exists():
    #             return Response("No procedure results found for the given definitions.", status=404)
    #         serializer = NewFlashTestSerializer(procedure_results, many=True, context={"request": request})
    #         return Response({"status": "success", "data": serializer.data})
    #     except Exception as e:
    #         return Response(f"An error occurred: {str(e)}", status=500)



        