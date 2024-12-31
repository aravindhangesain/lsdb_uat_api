from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from lsdb.models import ProcedureResult
from lsdb.serializers import GetProcedureDefinitionListSerializer

class GetProcedureDefinitionListViewSet(viewsets.ModelViewSet):
    queryset = ProcedureResult.objects.all()
    serializer_class = GetProcedureDefinitionListSerializer

    def get_queryset(self):
        workorder_id = self.request.query_params.get('workorder_id', None)
        if workorder_id:
            return ProcedureResult.objects.filter(work_order_id=workorder_id)
        return super().get_queryset()

    @action(detail=False, methods=["get"])
    def get_procedure_definitions(self, request, *args, **kwargs):
        workorder_id = request.query_params.get("workorder_id")
        if not workorder_id:
            return Response(
                {"error": "workorder_id query parameter is required."},
                status=400
            )
        results = ProcedureResult.objects.filter(work_order_id=workorder_id).values("procedure_definition_id")
        return Response({"procedure_definitions": list(results)})
