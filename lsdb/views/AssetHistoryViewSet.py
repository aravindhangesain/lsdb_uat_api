from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.models import *
from lsdb.serializers import * 

class AssetHistoryViewSet(viewsets.ModelViewSet):    
    queryset = ProcedureResult.objects.none()
    serializer_class = AssetHistorySerializer

    @action(detail=False, methods=['get'])
    def asset_list(self, request):
        self.context = {'request': request}
        assets = AssetCalibration.objects.all()
        response_data = []
        for asset in assets:
            if AssetSubAsset.objects.filter(asset_id=asset.id).exists():
                subasset_links = AssetSubAsset.objects.filter(asset_id=asset.id)
                subasset_ids = [link.sub_asset_id for link in subasset_links]
                subasset_names = AssetCalibration.objects.filter(
                    id__in=subasset_ids
                ).values_list("asset_name", flat=True)
                linked_date = subasset_links.first().linked_date if subasset_links.exists() else None
                in_use = asset.disposition_id == 7
                if in_use:
                    stress_runs = StressRunResult.objects.filter(
                        asset_id=asset.id, disposition_id=7
                    )
                else:
                    stress_runs = StressRunResult.objects.filter(
                        asset_id=asset.id, disposition_id=20
                    )
                procedure_result_ids = [run.procedure_result_id for run in stress_runs]
                procedure_results = ProcedureResult.objects.filter(id__in=procedure_result_ids)
                unit_serials_set = set()
                for pr in procedure_results:
                    if hasattr(pr, "unit_id") and pr.unit:
                        unit_serials_set.add(pr.unit.serial_number)
                    elif hasattr(pr, "units"):
                        unit_serials_set.update(pr.units.values_list("serial_number", flat=True))
                stressrun_data = []
                for run in stress_runs:
                    pr = procedure_results.filter(id=run.procedure_result_id).first()
                    if not pr:
                        continue
                    stressrun_data.append({
                        "run_name": run.run_name,
                        "units": list(unit_serials_set),
                        "start_date": pr.start_datetime,
                        "end_date": pr.end_datetime,
                        "procedure_definition": pr.procedure_definition.name if pr.procedure_definition else None
                    })
                response_data.append({
                    "id": asset.id,
                    "asset_name": asset.asset_name,
                    "asset_number": asset.asset_number,
                    "linkedsubassets": len(subasset_ids),
                    "linked_date": linked_date,
                    "subassets": list(subasset_names),
                    "inUse": in_use,
                    "stressrun_results": stressrun_data
                })
        return Response(response_data, status=status.HTTP_200_OK)


    # @transaction.atomic
    # @action(detail=False, methods=['get', 'post'])
    # def completed_units(self, request, pk=None):
    #     """
    #     Returns a list of completed units for a given asset, grouped by end_datetime.
    #     Asset ID's and corresponding Assets:
    #     82 - PVEL-001
    #     83 - PVEL-002
    #     84 - PVEL-003
    #     85 - PVEL-004   
    #     86 - PVEL-005
    #     87 - PVEL-006
    #     88 - PVEL-007
    #     89 - PVEL-008
    #     92 - Napa LUV 1
    #     93 - Napa LUV 2
    #     """
    #     self.context = {'request': request}
    #     disposition = Disposition.objects.get(id=20)
    #     asset_id = request.query_params.get('asset_id') 
    #     start_date = request.query_params.get('start_date') 
    #     end_date = request.query_params.get('end_date')
    #     start_dt = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    #     end_dt = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
    #     if not asset_id:
    #         return Response(
    #             {"detail": "asset_id is required in query params (?asset_id=123)."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     stepresult_qs = StepResult.objects.exclude(
    #         name__iexact="test start"
    #     )
    #     queryset = ProcedureResult.objects.filter(
    #         disposition=disposition,
    #         stepresult__measurementresult__asset__id=asset_id,
    #         stepresult__disposition__isnull=False
    #     ).prefetch_related(
    #         Prefetch("stepresult_set", queryset=stepresult_qs)
    #     ).distinct()
    #     if start_dt and end_dt:
    #         queryset = queryset.filter(
    #             start_datetime__gte=start_dt,
    #             end_datetime__lte=end_dt
    #         )
    #     serialized = AssetHistorySerializer(queryset, many=True, context=self.context).data
    #     # --- Group by end_datetime ---
    #     grouped = defaultdict(lambda: defaultdict(list))
    #     for item in serialized:
    #         end_dt = item.get("end_datetime")
    #         proc_name = item.get("procedure_definition_name")
    #         grouped[end_dt][proc_name].append(item)
    #     return Response(grouped, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["get"], url_path='download_completed_units')
    # def download_completed_units(self, request):
    #     asset_id = request.query_params.get('asset_id')
    #     if not asset_id:
    #         return Response(
    #             {"detail": "asset_id is required in query params (?asset_id=123)."},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     # --- Call completed_units internally ---
    #     response = self.completed_units(request)
    #     if response.status_code != status.HTTP_200_OK:
    #         return response  # just bubble up the same error/detail
    #     data = response.data  # this is already grouped by end_datetime
    #     if not data:
    #         return Response({"detail": "No data to export."}, status=status.HTTP_400_BAD_REQUEST)
    #     # --- Build CSV from completed_units output ---
    #     http_response = HttpResponse(content_type='text/csv')
    #     http_response['Content-Disposition'] = 'attachment; filename="CompletedUnits.csv"'
    #     writer = csv.writer(http_response)
    #     # write headers dynamically from first row
    #     sample_group = next(iter(data.values())) if isinstance(data, dict) else data
    #     if sample_group:
    #         headers = list(sample_group[0].keys())
    #         writer.writerow(headers)
    #         for end_time, items in data.items():
    #             for item in items:
    #                 row = [item.get(h) for h in sample_group[0].keys()]
    #                 writer.writerow(row)
    #     return http_response
