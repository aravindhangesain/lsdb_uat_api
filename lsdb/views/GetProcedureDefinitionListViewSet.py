from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from lsdb.models import ProcedureResult, ProcedureDefinition
from lsdb.serializers import GetProcedureDefinitionListSerializer

class GetProcedureDefinitionListViewSet(viewsets.ModelViewSet):
    queryset = ProcedureResult.objects.all()
    serializer_class = GetProcedureDefinitionListSerializer

    def get_queryset(self):
        workorder_id = self.request.query_params.get('workorder_id')
        if workorder_id:
            return ProcedureResult.objects.filter(work_order_id=workorder_id)
        return super().get_queryset()

    @action(detail=False, methods=["get"])
    def get_procedure_definitions(self, request, *args, **kwargs):
        workorder_id = request.query_params.get("workorder_id")
        if not workorder_id:
            return Response({"error": "workorder_id is required"}, status=400)
        distinct_procedure_definition_sequences = (
            ProcedureResult.objects.filter(work_order_id=workorder_id)
            .values_list("procedure_definition_id", flat=True)
            .distinct()
        )
        procedure_definitions = ProcedureDefinition.objects.filter(
            id__in=distinct_procedure_definition_sequences
        ).values("id", "name")
        return Response({
            "procedure_definitions": list(procedure_definitions)
        })
