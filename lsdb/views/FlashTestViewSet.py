from rest_framework import viewsets
from rest_framework.response import Response
from django_filters import rest_framework as filters
from lsdb.models import ProcedureResult
from lsdb.models import StepResult, MeasurementCorrectionFactor
from lsdb.models import MeasurementResult
from lsdb.serializers.ProcedureResultSerializer import FlashTestSerializer
import pandas as pd
from io import StringIO
from django.http import HttpResponse
from rest_framework.decorators import action
from django.db import transaction
from datetime import datetime
from django.utils import timezone
from datetime import datetime


class FlashTestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FlashTestSerializer
    pagination_class = None
    filter_backends = [filters.DjangoFilterBackend]


    def get_queryset(self):
        start_datetime_after = self.request.query_params.get('start_datetime_after', None)
        start_datetime_before = self.request.query_params.get('start_datetime_before', None)

        start_date = timezone.make_aware(datetime.strptime(start_datetime_after, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(start_datetime_before+' 23:59:59.999999', '%Y-%m-%d %H:%M:%S.%f'))
        
        # Django ORM QuerySet
        queryset = ProcedureResult.objects.filter(
            stepresult__measurementresult__date_time__range=(start_date, end_date),
            stepresult__measurementresult__measurement_definition_id__in=[51, 52, 53, 54, 55],
            stepresult__measurementresult__date_time__isnull=False,
            stepresult__measurementresult__result_double__isnull=False
        ).distinct().order_by('stepresult__measurementresult__date_time')
        
        return queryset

    @action(detail=False, methods=['get'], url_path='download')
    def download(self, request, *args, **kwargs):
        # Apply the filters from the query parameters
        queryset = self.filter_queryset(self.get_queryset())

        # Serialize the filtered data
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Specify the fields you want to include in the CSV
        selected_fields = [
            'unit_serial_number',
            # 'flash_start_datetime'
        ]  # Add other fields you want to include

        # Add the specific fields from module_property you want to include
        module_property_fields = ['module_property_id', 'isc', 'voc', 'module_width',
                                  'module_height']  # Replace with the two desired fields

        # Filter the data to include only the selected fields and the specific module_property fields
        filtered_data = []
        for item in data:
            filtered_item = {field: item[field] for field in selected_fields}
            if item['module_property']:
                for prop in module_property_fields:
                    filtered_item[prop] = item['module_property'].get(prop, None)
            filtered_data.append(filtered_item)

        # Convert the filtered data to a pandas DataFrame
        df = pd.DataFrame(filtered_data)

        # Create a StringIO buffer to save the CSV file
        buffer = StringIO()
        df.to_csv(buffer, index=False)

        # Seek to the beginning of the stream
        buffer.seek(0)

        # Create the HttpResponse with the appropriate content_type
        response = HttpResponse(buffer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Flash_Test_Results.csv'

        return response

    @action(detail=False, methods=['put'], url_path='update-measurement')
    def update_measurement(self, request):
        procedureresult_ids = request.data.get('procedureresult_id', [])
        update_data = request.data.get('update_data', {})

        with transaction.atomic():
            for procedureresult_id in procedureresult_ids:
                print(procedureresult_id)
                # Fetching the old ProcedureResult
                result = ProcedureResult.objects.get(id=procedureresult_id)
                execution = result.procedure_definition
                disposition = result.disposition

                # Create a new ProcedureResult based on the old one
                new_procedure_result = ProcedureResult.objects.create(
                    start_datetime=result.start_datetime,
                    end_datetime=result.end_datetime,
                    unit=result.unit,
                    name=result.name,
                    work_in_progress_must_comply=result.work_in_progress_must_comply,
                    disposition=result.disposition,
                    group=result.group,
                    work_order=result.work_order,
                    procedure_definition=execution,
                    version=result.version,
                    procedure_definition_id=result.procedure_definition_id,
                    linear_execution_group=result.linear_execution_group,
                    test_sequence_definition=result.test_sequence_definition,
                    allow_skip=result.allow_skip,   
                )

                # Copy all StepResults and MeasurementResults from the old ProcedureResult to the new one
                for old_step_result in result.stepresult_set.all():
                    # Create a new StepResult based on the old one
                    new_step_result = StepResult.objects.create(
                        name=old_step_result.name,
                        procedure_result=new_procedure_result,
                        step_definition=old_step_result.step_definition,
                        execution_number=old_step_result.execution_number,
                        disposition=old_step_result.disposition,
                        start_datetime=old_step_result.start_datetime,
                        duration=old_step_result.duration,
                        test_step_result=old_step_result.test_step_result,
                        archived=old_step_result.archived,
                        description=old_step_result.description,
                        step_number=old_step_result.step_number,
                        step_type=old_step_result.step_type,
                        linear_execution_group=old_step_result.linear_execution_group,
                        allow_skip=old_step_result.allow_skip,
                        notes=old_step_result.notes,  
                        procedure_result_id=new_procedure_result.id, 
                    )

                    # Copy all MeasurementResults from the old StepResult to the new one
                    for old_measurement_result in old_step_result.measurementresult_set.all():
                            if old_measurement_result.name in ["Pmp","Voc","Vmp","Isc","Imp"]:  
                                updated_value = float(update_data[old_measurement_result.name])
                                new_result_double = old_measurement_result.result_double / updated_value
                            else:
                                # If the name doesn't match, keep the old result_double value
                                new_result_double = old_measurement_result.result_double
                            MeasurementResult.objects.create(
                                step_result=new_step_result,
                                measurement_definition=old_measurement_result.measurement_definition,
                                software_revision=old_measurement_result.software_revision,
                                disposition=old_measurement_result.disposition,
                                limit=old_measurement_result.limit,
                                station=old_measurement_result.station,
                                name=old_measurement_result.name,
                                record_only=old_measurement_result.record_only,
                                allow_skip=old_measurement_result.allow_skip,
                                requires_review=old_measurement_result.requires_review,
                                measurement_type=old_measurement_result.measurement_type,
                                order=old_measurement_result.order,
                                report_order=old_measurement_result.report_order,
                                measurement_result_type=old_measurement_result.measurement_result_type,
                                result_double=new_result_double,
                                date_time=old_measurement_result.date_time,
                                result_datetime=old_measurement_result.result_datetime,
                                result_string=old_measurement_result.result_string,
                                result_boolean=old_measurement_result.result_boolean,
                                review_datetime=timezone.now(),
                                reviewed_by_user_id=self.request.user.id,
                                notes=old_measurement_result.notes,
                                tag=old_measurement_result.tag,
                                start_datetime=old_measurement_result.start_datetime,
                                duration=old_measurement_result.duration,
                                do_not_include=old_measurement_result.do_not_include,
                                asset_id=old_measurement_result.asset_id,
                                location_id=old_measurement_result.location_id,
                                result_defect_id=old_measurement_result.result_defect_id,
                                
                                user_id=old_measurement_result.user_id
                            )

                # Mark the old ProcedureResult as superseded
                result.supersede = True
                result.save()
                ProcedureResult.objects.filter(id=procedureresult_id).update(disposition_id=26)
                MeasurementCorrectionFactor.objects.create(new_procedure_result_id=new_procedure_result.id,old_procedure_result_id=procedureresult_id)
                print(f"Old ProcedureResult {procedureresult_id} superseded.")
                print(f"New ProcedureResult {new_procedure_result.id} created.")
                
        return Response('success')