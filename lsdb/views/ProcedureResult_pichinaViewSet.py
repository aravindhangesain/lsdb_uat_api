from rest_framework.response import Response
from rest_framework import viewsets
from lsdb.models import MeasurementResult_pichina, ProcedureResult_pichina
from lsdb.serializers import ProcedureWorkLog_pichinaSerializer, Procedureresult_pichinaSerializer, TransformIVCurve_pichinaSerializer
from lsdb.permissions import ConfiguredPermission
from rest_framework.decorators import action
from django.db.models import Q, Max
from django.utils import timezone
from datetime import datetime, timedelta, date
import pandas as pd



class ProcedureResult_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ProcedureResult_pichina.objects.all()
    serializer_class = Procedureresult_pichinaSerializer
    permission_classes = [ConfiguredPermission]

    @action(detail=True,methods=['get'],
        permission_classes=(ConfiguredPermission,),
        serializer_class=ProcedureWorkLog_pichinaSerializer)
    def view(self, request, pk=None):
        self.context = {'request':request}
        result = ProcedureResult_pichina.objects.get(id=pk)
        visualized={}
        try:
            visualized = getattr(self, "_view_{}".format(result.procedure_definition.visualizer.name))(request, pk)
        except:
            'some error'
        try:
            previous_result = ProcedureResult_pichina.objects.filter(
                linear_execution_group__lt=result.linear_execution_group,
                procedure_definition=result.procedure_definition,
                unit_id=result.unit_id,
                test_sequence_definition=result.test_sequence_definition,
                name__icontains="Pre"
            ).order_by('-linear_execution_group').first()

            flash_measurements = MeasurementResult_pichina.objects.filter(
                step_result__procedure_result=previous_result.id,
                measurement_result_type__name__icontains='result_double'
            )
            flash = {}
            for measurement in flash_measurements:
                flash[measurement.name] = measurement.result_double
            visualized['previous_test'] = {
                'pre_execution':previous_result.linear_execution_group,
                'prev_id' : previous_result.id,
                'prev_name' : previous_result.name,
                'flash_values': flash
            }
        except Exception as e:
            print(f"Error in visualizer: {e}")

        return Response(visualized)
    
    # Base visualizers:
    def _view_colorimeter(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_diode(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_el_image(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_iam(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_pan(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_visual_inspection(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_wet_leakage(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)

    # Transforming Visualizers
    def _view_stress(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = Procedureresult_pichinaSerializer(result, many=False, context=self.context)
        return (serializer.data)
    def _view_iv_curve(self, request, pk=None):
        result = ProcedureResult_pichina.objects.get(id=pk)
        serializer = TransformIVCurve_pichinaSerializer(result, many=False, context=self.context)
        return serializer.data
    

    @action(detail=False, methods=['get'],
        permission_classes=(ConfiguredPermission,),
        serializer_class=ProcedureWorkLog_pichinaSerializer)
    def procedure_stats(self, request, pk=None):
        self.context = {'request': request}
        file = request.query_params.get('file', 'dummy')
        start_datetime = request.query_params.get('start_datetime', 0)
        end_datetime = request.query_params.get('end_datetime', 0)
        # default to trailing 30 days
        days = request.query_params.get('days', 30)
        facility = request.query_params.get('facility', None)
        if start_datetime == 0 and end_datetime == 0:
            start_datetime = timezone.now() - timedelta(days=int(days))
            end_datetime = timezone.now()
        else:
            start_datetime = datetime.fromisoformat(start_datetime) + timedelta(days=1, hours=8)
            end_datetime = datetime.fromisoformat(end_datetime) + timedelta(days=1, hours=8)
            # this is still in zulu
        queryset = ProcedureResult_pichina.objects.filter(
            disposition__isnull=False,
            stepresult_pichina__archived=False,
            stepresult_pichina__disposition__isnull=False,
            stepresult_pichina__measurementresult_pichina__date_time__gte=start_datetime,
            stepresult_pichina__measurementresult_pichina__date_time__lte=end_datetime,
        ).distinct()
        if facility:
            queryset = queryset.filter(
                stepresult_pichina__measurementresult_pichina__asset__location__name=facility
            )
        queryset = queryset.annotate(
            last_result=Max('stepresult_pichina__measurementresult_pichina__date_time')
        )
        master_data_frame = pd.DataFrame(
            list(queryset.values('last_result', 'procedure_definition__name'))
        )
        master_data_frame['last_result'] = master_data_frame['last_result'].dt.tz_convert("US/Pacific")
        master_data_frame['last_result'] = master_data_frame['last_result'].dt.date
        df1 = pd.crosstab(
            master_data_frame['procedure_definition__name'],
            master_data_frame['last_result'].fillna(0)
        )
        final = []
        my_dict = df1.to_dict()
        for day in my_dict:
            row = {'date': day}
            row.update(my_dict[day].items())
            final.append(row)
        return Response(final)

        