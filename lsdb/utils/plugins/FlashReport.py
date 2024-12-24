class FlashReport():
    import zipfile
    import numpy as np
    import datetime
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter
    from io import BytesIO
    from django.db import IntegrityError, transaction
    from django.http import FileResponse, HttpResponse
    from django.utils import timezone
    from lsdb.utils import ExcelFile
    from django.db.models import Q, Sum, Max, Min, F
    from rest_framework.response import Response
    from lsdb.serializers.WorkOrderSerializer import WorkOrderSerializer
    from lsdb.models import Disposition
    from lsdb.models import MeasurementResult
    from lsdb.models import ProcedureResult
    from lsdb.models import TestSequenceDefinition
    from lsdb.models import Project
    from lsdb.models import Unit
    from lsdb.models import WorkOrder

    def __init__(self):
        self.ids = [1]

    def _test(self):
        pass

    def _run(self, project_number:str):
        mem_zip = self.BytesIO()
        with self.zipfile.ZipFile(mem_zip, mode='w', compression=self.zipfile.ZIP_DEFLATED) as zf:
            work_orders = self.Project.objects.get(number=project_number).workorder_set.all()
            for work_order in work_orders:
                sheets = []
                excel_file_flash = self.ExcelFile()
                flash_sheet = excel_file_flash.workbook.active
                flash_sheet.append(
                    ["Serial Number", "TSD", "LEG", "Pmp", "Voc", "Vmp", "Isc", "Imp", "Irradiance", "Temperature"])
                sheets.append(flash_sheet)
                results = self.ProcedureResult.objects.filter(work_order=work_order,
                    disposition__isnull=False)\
                    .select_related('test_sequence_definition')\
                    .select_related('procedure_definition')\
                    .select_related('unit')\
                    .prefetch_related('stepresult_set__measurementresult_set')
                for test in results:
                    if "I-V" in test.procedure_definition.name:
                        for step_result in test.stepresult_set.all().exclude(archived=True):
                            data = [test.unit.serial_number, test.test_sequence_definition.name, test.name]
                            for measurement in step_result.measurementresult_set.all().order_by('report_order'):
                                if measurement.measurement_result_type.name == 'result_files':
                                    continue
                                elif measurement.measurement_result_type.name == 'result_datetime':
                                    continue
                                else:
                                    data.append(getattr(measurement, measurement.measurement_result_type.name))
                            flash_sheet.append(data)
            for sheet in sheets:
                dims = {}
                for row in sheet.rows:
                    for cell in row:
                        if cell.value:
                            dims[cell.column_letter] = max(
                                (dims.get(cell.column_letter, 0), len(str(cell.value))))
                for col, value in dims.items():
                    sheet.column_dimensions[col].width = value

            zf.writestr('{}/{}/{}'.format(work_order.project.number, work_order.name, "Flash.xlsx"),
                        excel_file_flash.get_memory_file().read())

        filename = self.timezone.now().strftime('%b-%d-%Y-%H%M%S')
        response = self.HttpResponse(mem_zip.getvalue(), content_type='application/x-zip-compressed')
        response['Content-Disposition'] = f'attachment; filename={filename}.zip'
        return response
