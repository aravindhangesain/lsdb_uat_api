class CorrectIVCurve():
    from django.db import IntegrityError
    """
    This plugin accepts a Unit serial, an I-V curve Procedure Definition ID,
    an Execution Group number, and a set of correction factors to be applied to
    Pmp, Voc, Vmp, Isc, and Imp.
    It first finds the Unit, then the Procedure Result corresponding to the
    Procedure Definition and Execution Group (guaranteed unique),
    and triggers a retest of that Procedure Result.
    From the original Procedure Result and correction factors, it calculates
    the corrected measurement values and submits them to the retested
    Procedure Result.
    To use this plugin:
    POST {
        "user":111,
        "serial":"serial_number_here",
        "proc_defn":123,
        "eg_number":7,
        "correction_factors":{"Pmp":1.001, "Voc":0.999, "Vmp":1.011, "Isc":0.990, "Imp":0.987}
        }
    """
    def __init__(self:object):
        pass


    def _test(self:object):
        return(None)

    def _run(self:object, user:int=None, serial:str=None, proc_defn:int=None, eg_number:int=None, correction_factors:dict={}):
        import json
        import csv
        import io
        import hashlib

        from lsdb.models import Unit
        from lsdb.models import ProcedureDefinition
        from lsdb.models import ProcedureResult
        from lsdb.models import StepResult
        from lsdb.models import MeasurementResult
        from lsdb.models import AzureFile

        from lsdb.views import ProcedureResultViewSet
        from lsdb.views import StepResultViewSet
        from lsdb.views import MeasurementResultViewSet

        from lsdb.utils import RetestUtils
        from lsdb.utils.NoteUtils import create_note

        from django.contrib.auth.models import User

        from django.test.client import RequestFactory

        from django.core.exceptions import ObjectDoesNotExist
        from django.core.files import File

        try:
            unit = Unit.objects.get(serial_number=serial)
        except ObjectDoesNotExist:
            return {'Error':'Unit {} not found'.format(self.serial)}

        # Should return exactly one Procedure Result
        proc_result_list = unit.procedureresult_set.filter(linear_execution_group=eg_number, procedure_definition=proc_defn, disposition__isnull=False)
        if len(proc_result_list) != 1:
            return {'Error':'{} Procedure Results found'.format(len(proc_result_list))}
        original_proc_result = proc_result_list[0]

        # ...which should have exactly one Step Result
        original_step_result_list = original_proc_result.stepresult_set.all()
        if len(original_step_result_list) != 1:
            return {'Error':'{} Step Results found'.format(len(original_step_result_list))}
        original_step_result = original_step_result_list[0]

        # Find its data files, and create a new data file to insert into the new Procedure Result
        # Measurement Definition ID 90 "Data File" hard-coded
        file_meas_result_list = original_step_result.measurementresult_set.filter(measurement_definition=79)

        # Compile all attached files, regardless of structure
        azure_file_list = []
        for file_meas_result in file_meas_result_list:
            azure_file_list.extend(file_meas_result.result_files.all())

        # If only one file is present, use it
        if len(azure_file_list) == 1:
            original_file = azure_file_list[0]
        # Otherwise, look for a "Results" file
        else:
            for azure_file in azure_file_list:
                if "_Results_" in azure_file.name:
                    original_file = azure_file.file
                    original_file_name = azure_file.name
                    break
            else:
                return {'Error':'Results file not found'}

        # Read in the data from the AzureFile
        csv_data = []
        with io.BytesIO() as original_file_buffer:
            for buf in original_file.file.chunks(chunk_size=65536):
                original_file_buffer.write(buf)
            original_file_buffer.seek(0)
            with io.TextIOWrapper(original_file_buffer, encoding="utf-8", newline='', write_through=True) as csv_file:
                reader = csv.reader(csv_file, dialect='excel-tab')
                for row in reader:
                    csv_data.append(row)

        # Add a note signifying corrected data
        csv_data[0][15] = 'CORRECTED'

        # Remove any I-V curve data
        for row in csv_data[1:]:
            row[0:6] = ['']*6

        # Remove Rshunt and Rseries values, if present
        csv_data[4][12] = csv_data[4][13] = 'NaN'

        # Replace derived parameters with corrected values
        # Define order of derived parameters in data file
        param_order = ["Pmp", "Voc", "Vmp", "Isc", "Imp"]
        for meas_result in original_step_result.measurementresult_set.all():
            if meas_result.name in param_order:
                csv_data[4][7+param_order.index(meas_result.name)] = str(meas_result.result_double * correction_factors[meas_result.name])

        # Write the file to buffer, and save for upload later
        new_file = io.BytesIO()
        csv_file = io.TextIOWrapper(new_file, encoding="utf-8", newline='', write_through=True)
        writer = csv.writer(csv_file, dialect='excel-tab')
        for row in csv_data:
            writer.writerow(row)

        # Spoof an HttpRequest object
        rf = RequestFactory()
        request = rf.post('/nopath/', data={}, content_type="application/json")
        request.user = User.objects.get(id=user)
        request.META['SERVER_NAME'] = '127.0.0.1'

        # Send empty request to retest_procedure()
        retest = RetestUtils()
        response = retest.retest_procedure(request=request, pk=original_proc_result.id)
        new_proc_result = ProcedureResult.objects.get(id=response['id'])

        # Load up request body for submitting Results
        submit_data = json.loads('{}')
        submit_data['historic'] = True
        submit_data['user'] = user
        submit_data['disposition'] = 4 # "Performed - Record Only"

        # Instantiate viewsets
        proc_result_view = ProcedureResultViewSet()
        step_result_view = StepResultViewSet()
        meas_result_view = MeasurementResultViewSet()

        # Only one Step Result should be created
        new_step_result_list = new_proc_result.stepresult_set.all()
        if len(new_step_result_list) != 1:
            return {'Error':'{} Step Results created'.format(len(new_step_result_list))}
        new_step_result = new_step_result_list[0]

        for new_meas_result in new_step_result.measurementresult_set.all():
            original_meas_result = original_step_result.measurementresult_set.filter(measurement_definition=new_meas_result.measurement_definition)[0]
            # Apply correction factor (if present) to both Measurement Result and file data
            if new_meas_result.name in correction_factors:
                submit_data['result_double'] = original_meas_result.result_double * correction_factors[new_meas_result.name]
            else:
                submit_data['result_double'] = original_meas_result.result_double
            # Write the new data file
            if new_meas_result.measurement_definition.id == 79:
                django_file = File(new_file)
                django_file.name = original_file_name
                hasher = hashlib.new('sha256')
                for buf in django_file.chunks(chunk_size=65536):
                    hasher.update(buf)
                azure_file = AzureFile.objects.create(
                    file = django_file,
                    name = django_file.name,
                    hash_algorithm = 'sha256',
                    hash = hasher.hexdigest(),
                    length=django_file.size
                    )
                link_file_data = json.loads('{}')
                link_file_data['id'] = azure_file.id
                request.data = link_file_data
                meas_result_view.link_files(request, pk=new_meas_result.id)
            if original_meas_result.asset:
                submit_data['asset'] = original_meas_result.asset.id
            if original_meas_result.start_datetime:
                submit_data['start_datetime'] = str(original_meas_result.start_datetime)
            request.data = submit_data
            meas_result_view.submit(request, pk=new_meas_result.id)
        # Submit Step Result after all Measurement Results
        step_result_view.submit(request, pk=new_step_result.id)
        # Submit Procedure Result after all Step Results
        proc_result_view.submit(request, pk=new_proc_result.id)

        # Set base Note parameters
        note_params = {'model':'procedureresult','note_type':1,'user':request.user}
        note_params['subject'] = "Post-Transit Corrections"
        # Add a Note to the original Procedure Result
        note_params['pk'] = original_proc_result.id
        note_params['text'] = "Correction factors have been calculated for these results; please see the superseding Procedure Result for corrected data."
        create_note(**note_params)
        # Add a note to the new Procedure Result
        note_params['pk'] = new_proc_result.id
        note_params['text'] = "Correction factors have been applied to these results; please see the project folder on Box for additional details."
        create_note(**note_params)

        return None
