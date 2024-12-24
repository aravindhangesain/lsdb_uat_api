class ELFlashDump():
    '''
    This plugin was initially written to collect all EL and I-V curve files from a
    specific test sequence. It emits a .csv file containing all of the files. This
    file may be used to direct a download scrip, or a Box.com transport script to
    facilitate external sharing. The file will be named with a .zip extension and must be changed.
    Usage:
    Serialize must be diabled.
    Input Variables:
        tsd:Test sequence Definfiton ID (list int, optional)
        project: Project Name (list str, optional)

    example:
        {
            "tsd":[126,6],
            "project":["6677","8765"]
        }
    This would return all files attached to tests in TSDs 126 OR 6 from projects "6677" OR "8765"
    '''
    def __init__(self:object):
        pass

    def _test(self:object, tsd:list=None, project:list=None):
        pass

    def _run(self:object,  tsd:list=None, project:list=None):
        import hashlib
        import zipfile
        import pandas as pd
        from io import BytesIO

        from lsdb.models import AzureFile
        from lsdb.models import ProcedureResult
        from lsdb.utils import DeferredFile
        from django.http import FileResponse, HttpResponse
        from django.utils import timezone
        from django.db.models import Q, Max

        # results = ProcedureResult.objects.filter( Q(test_sequence_definition__id__in=[126,6],
        #     stepresult__measurementresult__result_files__length__gt=0, disposition__isnull=False),
        #     Q(procedure_definition__name__icontains='EL Image at') | Q (procedure_definition__name__icontains='I-V'))

        allfiles = AzureFile.objects.filter(
            Q(measurementresult__step_result__procedure_result__procedure_definition__name__icontains='EL Image at') | Q (measurementresult__step_result__procedure_result__procedure_definition__name__icontains='I-V')).distinct()
        if tsd:
            allfiles = allfiles.filter(Q(measurementresult__step_result__procedure_result__test_sequence_definition__id__in=tsd,
            measurementresult__step_result__procedure_result__disposition__isnull=False)).distinct()
        if project:
            allfiles = allfiles.filter(Q(measurementresult__step_result__procedure_result__work_order__project__number__in=project,
            measurementresult__step_result__procedure_result__disposition__isnull=False)).distinct()
        allfiles = allfiles.annotate(parent_procedure=Max('measurementresult__step_result__procedure_result__name'))
        master_data_frame = pd.DataFrame(list(allfiles.values(
            'id',
            'name',
            'parent_procedure'
        )))
        mem_csv = BytesIO()
        master_data_frame.to_csv(mem_csv)
        # if file_count:
        #     allfiles = allfiles[:file_count]

        # mem_zip = BytesIO()
        # with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        #     for azurefile in allfiles:
        #         bytes = azurefile.file.file.read()
        #         zf.writestr('{}/{}'.format(
        #             azurefile.parent_procedure,
        #             azurefile.file.name
        #         ),bytes)
        #         # return{'file_count':}


        filename=timezone.now().strftime('%b-%d-%Y-%H%M%S')
        # response = HttpResponse(mem_zip.getvalue(), content_type='application/x-zip-compressed')
        # response['Content-Disposition'] = 'attachment; filename={}.zip'.format(filename)
        response = HttpResponse(mem_csv.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
        return response
