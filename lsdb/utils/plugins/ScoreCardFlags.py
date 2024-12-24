class ScoreCardFlags():
    import pandas as pd
    import datetime
    from openpyxl import Workbook
    from openpyxl.utils import get_column_letter
    from io import BytesIO

    from django.http import FileResponse, HttpResponse
    from django.utils import timezone
    from lsdb.utils import ExcelFile
    from django.db.models import Q, Sum, Max, Min, F
    from rest_framework.response import Response

    from lsdb.models import Note
    from lsdb.models import NoteType

    def __init__(self):
        self.base_url = "https://lsdb.pvel.com/engineering/engineering_agenda/"

    def _test(self):
        pass

    def _run(self, start_date=None, end_date=None):
        flagtype = self.NoteType.objects.get(name__iexact="task")
        # flagtype = self.NoteType.objects.get(name__iexact="note")
        #flagtype = self.NoteType.objects.get(name__iexact="flag")
        queryset = self.Note.objects.filter(note_type=flagtype, parent_note__isnull=True).distinct()
        queryset = queryset.annotate(
            disposition_name = self.Max('disposition__name'),
            project_number = self.Max('procedureresult__work_order__project__number'),
            tsd_name = self.Max('procedureresult__test_sequence_definition__name'),
            serial_number = self.Max('unit__serial_number'),
            characterization = self.Max('procedureresult__name'),
            )

        note_xls = self.ExcelFile()
        note_sheet = note_xls.workbook.active
        note_sheet.append(["URL","Disposition", "Project", "TSD","Serial Number", "Subject", "Body", "Labels", "Characterization"])

        for flag in queryset:
            labels = []
            for label in list(flag.labels.all().values('name')):
                labels.append(label.get('name'))
            note_sheet.append([
                "{}{}".format(self.base_url,flag.id),
                flag.disposition_name,
                flag.project_number,
                flag.tsd_name,
                flag.serial_number,
                flag.subject,
                flag.text,
                ','.join(labels),
                flag.characterization
                ])
        filename = 'ColorimeterReport-{}'.format(self.timezone.now().strftime('%b-%d-%Y-%H%M%S'))
        return note_xls.get_response(str(filename))
