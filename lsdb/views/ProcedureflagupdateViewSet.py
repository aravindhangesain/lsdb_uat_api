from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from lsdb.models import ProcedureDefinition, ProcedureResult, ProcedureResult_FinalResult
from lsdb.serializers import ProcedureResult_FinalResultSerializer

class ProcedureflagupdateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ProcedureResult to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ProcedureResult_FinalResult.objects.all()
    serializer_class = ProcedureResult_FinalResultSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        procedure_result_id = self.kwargs.get(self.lookup_field)
        try:
            # Retrieve the specific ProcedureResult instance
            procedure_result = ProcedureResult.objects.get(id=procedure_result_id)
            
            # Get related unit_id and procedure_definition_id
            unit_id = procedure_result.unit_id
            procedure_definition_id = procedure_result.procedure_definition_id
            
            # Get all ProcedureResults with the same unit_id and procedure_definition_id
            related_results = ProcedureResult.objects.filter(
                unit_id=unit_id,
                procedure_definition_id=procedure_definition_id
            )
            
            # Update final_result to False in the ProcedureResultFinalResult table for all related results
            ProcedureResult_FinalResult.objects.filter(
                procedure_result__in=related_results
            ).update(final_result=False)

            # Retrieve the ProcedureDefinition instance
            procedure_definition_instance = ProcedureDefinition.objects.get(id=procedure_definition_id)

            # Try to get the existing ProcedureResultFinalResult entry
            final_result_instance = ProcedureResult_FinalResult.objects.filter(
                procedure_result=procedure_result
            ).first()

            if final_result_instance is None:
                # If no existing entry, create a new one
                final_result_instance = ProcedureResult_FinalResult.objects.create(
                    procedure_result=procedure_result,
                    updated_date=timezone.now(),
                    procedure_definition=procedure_definition_instance,
                    final_result=request.data.get('final_result', False)  # Default to False if not provided
                )
            else:
                # If it exists, update the final_result and updated_date
                final_result_instance.final_result = request.data.get('final_result', final_result_instance.final_result)
                final_result_instance.updated_date = timezone.now()  # Always update the timestamp
                final_result_instance.save()  # Save the instance after updates

            # Serialize and return the updated ProcedureResultFinalResult
            serializer = self.get_serializer(final_result_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ProcedureResult.DoesNotExist:
            return Response({"error": "ProcedureResult not found."}, status=status.HTTP_404_NOT_FOUND)
