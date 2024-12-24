from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.models import MeasurementCorrectionFactor, StepResult, MeasurementResult,WorkOrder,Project,Customer,ProcedureResult
from lsdb.serializers import MeasurementCorrectionFactorSerializer
from rest_framework import viewsets
from django.http import HttpResponse
from openpyxl import Workbook

class MeasurementCorrectionFactorViewSet(viewsets.ModelViewSet):
    queryset = MeasurementCorrectionFactor.objects.all()
    serializer_class = MeasurementCorrectionFactorSerializer

    @action(detail=False, methods=['get'])
    def corrected_procedures(self, request):
        measurement_corrections = MeasurementCorrectionFactor.objects.all()
        corrected_procedures_list = []
        
        for correction in measurement_corrections:
            # Fetch all step results for the old procedure result ID
            old_stepresults = StepResult.objects.filter(
                procedure_result_id=correction.old_procedure_result_id
            )

            # Handle multiple step results if they exist
            for old_stepresult in old_stepresults:
                old_measurementresults = MeasurementResult.objects.filter(
                    step_result_id=old_stepresult.id,
                    name__in=["Imp", "Isc", "Vmp", "Voc", "Pmp"]
                )
                old_correction_factor = {
                    result.name: round(result.result_double, 2)
                    for result in old_measurementresults if result.result_double is not None
                }

                # Fetch all step results for the new procedure result ID
                new_stepresults = StepResult.objects.filter(
                    procedure_result_id=correction.new_procedure_result_id
                )

                # Handle multiple step results for the new procedure
                for new_stepresult in new_stepresults:
                    new_measurementresults = MeasurementResult.objects.filter(
                        step_result_id=new_stepresult.id,
                        name__in=["Imp", "Isc", "Vmp", "Voc", "Pmp"]
                    )
                    new_correction_factor = {
                        result.name: round(result.result_double, 2)
                        for result in new_measurementresults if result.result_double is not None
                    }

                    stepresult_id=old_stepresult.id
                    stepresult=StepResult.objects.get(id=stepresult_id)
                    work_order = stepresult.procedure_result.work_order
                    project = work_order.project
                    customer_name = project.customer.name

                    corrected_procedure_details = {
                        "id":correction.id,
                        "serial_number":old_stepresult.procedure_result.unit.serial_number,
                        "project_number":project.number,
                        "customer":customer_name,
                        "bom":work_order.name,
                        "old_procedure_result_id": correction.old_procedure_result_id,
                        "module_property_before_applying_correction_factor": old_correction_factor,
                        "new_procedure_result_id": correction.new_procedure_result_id,
                        "module_property_after_applying_correction_factor": new_correction_factor,
                    }

                    corrected_procedures_list.append(corrected_procedure_details)

        return Response(corrected_procedures_list)

    @action(detail=False, methods=['get'], url_path='corrected_procedures/download-excel')
    def download_excel(self, request):
        measurement_corrections = MeasurementCorrectionFactor.objects.all()

        # Create an Excel workbook and sheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Corrected Procedures"

        # Create the header row
        ws.append([
            "ID","Serial Number","Project Number","Customer Name","BOM", "Old Procedure Result ID", "Pmp (Before)", "Voc (Before)", "Vmp (Before)", 
            "Isc (Before)", "Imp (Before)", "New Procedure Result ID", "Pmp (After)", 
            "Voc (After)", "Vmp (After)", "Isc (After)", "Imp (After)"
        ])

        # Loop through the corrections and populate the sheet
        for correction in measurement_corrections:
            old_stepresults = StepResult.objects.filter(
                procedure_result_id=correction.old_procedure_result_id
            )

            for old_stepresult in old_stepresults:
                old_measurementresults = MeasurementResult.objects.filter(
                    step_result_id=old_stepresult.id,
                    name__in=["Imp", "Isc", "Vmp", "Voc", "Pmp"]
                )
                old_correction_factor = {
                    result.name: round(result.result_double, 2)
                    for result in old_measurementresults if result.result_double is not None
                }

                new_stepresults = StepResult.objects.filter(
                    procedure_result_id=correction.new_procedure_result_id
                )

                for new_stepresult in new_stepresults:
                    new_measurementresults = MeasurementResult.objects.filter(
                        step_result_id=new_stepresult.id,
                        name__in=["Imp", "Isc", "Vmp", "Voc", "Pmp"]
                    )
                    new_correction_factor = {
                        result.name: round(result.result_double, 2)
                        for result in new_measurementresults if result.result_double is not None
                    }

                    stepresult_id=old_stepresult.id
                    stepresult=StepResult.objects.get(id=stepresult_id)
                    work_order = stepresult.procedure_result.work_order
                    project = work_order.project
                    customer_name = project.customer.name


                    # Populate the row for each procedure result
                    ws.append([
                        correction.id,
                        old_stepresult.procedure_result.unit.serial_number,
                        project.number,
                        customer_name,
                        work_order.name,
                        correction.old_procedure_result_id,
                        old_correction_factor.get("Pmp", ""),
                        old_correction_factor.get("Voc", ""),
                        old_correction_factor.get("Vmp", ""),
                        old_correction_factor.get("Isc", ""),
                        old_correction_factor.get("Imp", ""),
                        correction.new_procedure_result_id,
                        new_correction_factor.get("Pmp", ""),
                        new_correction_factor.get("Voc", ""),
                        new_correction_factor.get("Vmp", ""),
                        new_correction_factor.get("Isc", ""),
                        new_correction_factor.get("Imp", ""),
                    ])

        # Prepare the HttpResponse for the file download
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="corrected_procedures.xlsx"'

        # Save the workbook to the HttpResponse
        wb.save(response)
        return response