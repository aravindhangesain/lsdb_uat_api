# Plugin from production
class ColorimeterValueReport():
    import pandas as pd
    import numpy as np
    import json
    import datetime
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter
    from io import BytesIO

    from django.http import FileResponse, HttpResponse
    from django.utils import timezone
    from lsdb.utils import ExcelFile
    from django.db.models import Q, Sum, Max, Min, F
    from rest_framework.response import Response

    from lsdb.models import MeasurementResult

    def __init__(self):
        pass

    def _test(self):
        pass

    def _run(self, start_date=None, end_date=None):
        queryset = self.MeasurementResult.objects.filter(asset__asset_types__name='Colorimeter').distinct()
        note_xls = self.ExcelFile()
        note_sheet = note_xls.workbook.active
        note_sheet.append(["Project", "TSD","TSD Version","Serial Number",
            "Characterization","B val av", "B val std"])

        for result in queryset:
            blob = self.json.loads(result.result_string)
            df = self.pd.DataFrame(blob.get('values'))
            note_sheet.append([
                result.step_result.procedure_result.work_order.project.number,
                result.step_result.procedure_result.test_sequence_definition.name,
                result.step_result.procedure_result.test_sequence_definition.version,
                result.step_result.procedure_result.unit.serial_number,
                result.step_result.procedure_result.name,
                df.b_value.mean(),
                df.b_value.std(),
                ])
        filename = 'ColorimeterReport-{}'.format(self.timezone.now().strftime('%b-%d-%Y-%H%M%S'))
        return note_xls.get_response(str(filename))
