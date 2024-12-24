from rest_framework.response import Response
from rest_framework import viewsets
from lsdb.models import MeasurementResult_pichina, ProcedureResult_pichina
from lsdb.serializers import ProcedureWorkLog_pichinaSerializer, Procedureresult_pichinaSerializer, TransformIVCurve_pichinaSerializer
from lsdb.permissions import ConfiguredPermission
from rest_framework.decorators import action



class ProcedureResult_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ProcedureResult_pichina.objects.all()
    serializer_class = Procedureresult_pichinaSerializer
    permission_classes = [ConfiguredPermission]

    @action(detail=True,methods=['get'],
    permission_classes=(ConfiguredPermission,),
    serializer_class=ProcedureWorkLog_pichinaSerializer)
    def view(self, request, pk=None):
        # read the visualizer value of the current record to determine the shape
        # of the data to return.
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

    