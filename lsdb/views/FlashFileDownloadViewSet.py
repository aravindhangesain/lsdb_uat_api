from rest_framework import viewsets
from rest_framework.response import Response
from django.http import HttpResponse
from lsdb.models import ProcedureResult, StepResult, MeasurementResult,AzureFile
import magic
from rest_framework.decorators import action
from lsdb.permissions import ConfiguredPermission
from django.db import connection


class FlashFileDownloadViewSet(viewsets.ModelViewSet):
    queryset = ProcedureResult.objects.none()

    def get_serializer_class(self):
        return None

    @action(detail=True, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            )
    def download(self, request, pk=None):
        try:
            # Step 1: Get ProcedureResult by pk
            procedure_result = ProcedureResult.objects.get(id=pk)

            # Step 2: Get the associated StepResult
            step_result = StepResult.objects.get(procedure_result=procedure_result)

            # Step 3: Get the associated MeasurementResult using the step_result
            measurement_result = MeasurementResult.objects.filter(step_result=step_result,name='Data File').first()

            # Step 4: Get the MeasurementResultResultFiles entry where 'Data file' matches using raw SQL
            query = """
                SELECT azurefile_id
                FROM lsdb_measurementresult_result_files
                WHERE measurementresult_id = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(query, [measurement_result.id])
                result = cursor.fetchone()

            if result is None:
                return Response({'error': "'Data file' not found in MeasurementResultResultFiles"}, status=404)

            # Step 5: Get the associated AzureFile entry using the azure_file_id
            azure_file_id = result[0]
            azure_file = AzureFile.objects.get(id=azure_file_id)
            file = azure_file.file

            # Open the file and determine its MIME type
            file_handle = file.open()
            content_type = magic.from_buffer(file_handle.read(2048), mime=True)

            # Step 6: Prepare the response to send the file as downloadable
            response = HttpResponse(file_handle, content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename={0}'.format(file)
            return response

        except ProcedureResult.DoesNotExist:
            return Response({'error': 'ProcedureResult not found'}, status=404)
        except StepResult.DoesNotExist:
            return Response({'error': 'StepResult not found for this ProcedureResult'}, status=404)
        except MeasurementResult.DoesNotExist:
            return Response({'error': 'MeasurementResult not found for this StepResult'}, status=404)
        except AzureFile.DoesNotExist:
            return Response({'error': 'AzureFile not found for the provided Azure file ID'}, status=404)