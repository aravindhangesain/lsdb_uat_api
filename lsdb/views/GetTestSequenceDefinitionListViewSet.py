from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from lsdb.models import ProcedureResult
from lsdb.serializers import GetTestSequenceDefinitionListSerializer

class GetTestSequenceDefinitionListViewSet(viewsets.ModelViewSet):
    queryset = ProcedureResult.objects.all()
    serializer_class = GetTestSequenceDefinitionListSerializer

    def get_queryset(self):
        workorder_id = self.request.query_params.get('workorder_id', None)
        if workorder_id:
            return ProcedureResult.objects.filter(work_order_id=workorder_id)
        return super().get_queryset()

    @action(detail=False, methods=["get"])
    def get_test_sequence_definitions(self, request, *args, **kwargs):
        workorder_id = request.query_params.get("workorder_id")
        results = ProcedureResult.objects.filter(work_order_id=workorder_id).values("test_sequence_definition_id")
        return Response({"test_sequence_definitions": list(results)})
