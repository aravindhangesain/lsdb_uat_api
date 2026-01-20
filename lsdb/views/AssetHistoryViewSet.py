from datetime import timezone
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.models import *
from lsdb.serializers import * 


class AssetHistoryViewSet(viewsets.ModelViewSet):    
    queryset = ProcedureResult.objects.none()
    
    def get_serializer_class(self):
        return None
    
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
                in_use = asset.disposition_id == 18
                if in_use:
                    stress_runs = StressRunResult.objects.filter(
                        asset_id=asset.id, disposition_id=18
                    )
                else:
                    stress_runs = StressRunResult.objects.filter(
                        asset_id=asset.id, disposition_id=20
                    )
                procedure_result_ids = [run.procedure_result_id for run in stress_runs]
                procedure_results = ProcedureResult.objects.filter(id__in=procedure_result_ids,group_id = 45)
                stressrun_data = []
                for run in stress_runs:
                    pr = procedure_results.filter(id=run.procedure_result_id).first()
                    if not pr:
                        continue
                    unit_serials = set()
                    if hasattr(pr, "unit") and pr.unit:
                        unit_serials.add(pr.unit.serial_number)
                    elif hasattr(pr, "units"):
                        unit_serials.update(pr.units.values_list("serial_number", flat=True))
                    stressrun_data.append({
                        "run_name": run.run_name,
                        "units": list(unit_serials),
                        "start_date": pr.start_datetime,
                        "end_date": pr.end_datetime,
                        "procedure_definition": pr.procedure_definition.name if pr.procedure_definition else None
                    })
                stressrun_data = sorted(stressrun_data,key=lambda x: x["start_date"] or timezone.datetime.min,reverse=True)
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


    # @action(detail=False, methods=['get'])
    # def asset_list(self, request):
    #     self.context = {'request': request}
    #     assets = AssetCalibration.objects.all()
    #     response_data = []
    #     for asset in assets:
    #         if AssetSubAsset.objects.filter(asset_id=asset.id).exists():
    #             subasset_links = AssetSubAsset.objects.filter(asset_id=asset.id)
    #             subasset_ids = [link.sub_asset_id for link in subasset_links]
    #             subasset_names = AssetCalibration.objects.filter(
    #                 id__in=subasset_ids
    #             ).values_list("asset_name", flat=True)
    #             linked_date = subasset_links.first().linked_date if subasset_links.exists() else None
    #             in_use = asset.disposition_id == 18
    #             disposition_value = 18 if in_use else 20
    #             stress_runs = StressRunResult.objects.filter(
    #                 asset_id=asset.id,
    #                 disposition_id=disposition_value
    #             )
    #             procedure_result_ids = [run.procedure_result_id for run in stress_runs]
    #             procedure_results = ProcedureResult.objects.filter(
    #                 id__in=procedure_result_ids,
    #                 group_id=45
    #             ).select_related("procedure_definition", "unit")
    #             unit_serials_set = set()
    #             for pr in procedure_results:
    #                 if hasattr(pr, "unit") and pr.unit:
    #                     unit_serials_set.add(pr.unit.serial_number)
    #                 elif hasattr(pr, "units"):
    #                     unit_serials_set.update(
    #                         pr.units.values_list("serial_number", flat=True)
    #                     )
    #             stressrun_data = []
    #             latest_run_data = None
    #             procedure_definitions = set()
    #             for run in stress_runs:
    #                 pr = next((p for p in procedure_results if p.id == run.procedure_result_id), None)
    #                 if not pr:
    #                     continue
    #                 proc_name = pr.procedure_definition.name if pr.procedure_definition else None
    #                 if proc_name:
    #                     procedure_definitions.add(proc_name)
    #                 run_data = {
    #                     "run_name": run.run_name,
    #                     "units": list(unit_serials_set),
    #                     "start_date": pr.start_datetime,
    #                     "end_date": pr.end_datetime,
    #                     "procedure_definition": proc_name,
    #                 }
    #                 stressrun_data.append(run_data)
    #                 if not latest_run_data or (
    #                     pr.start_datetime and pr.start_datetime > latest_run_data["start_date"]
    #                 ):
    #                     latest_run_data = run_data
    #             response_data.append({
    #                 "id": asset.id,
    #                 "asset_name": asset.asset_name,
    #                 "asset_number": asset.asset_number,
    #                 "linkedsubassets": len(subasset_ids),
    #                 "linked_date": linked_date,
    #                 "subassets": list(subasset_names),
    #                 "inUse": in_use,
    #                 "latest_run_name": latest_run_data["run_name"] if latest_run_data else None,
    #                 "latest_procedure_definition": list(procedure_definitions),
    #                 "latest_start_date": latest_run_data["start_date"] if latest_run_data else None,
    #                 "latest_end_date": latest_run_data["end_date"] if latest_run_data else None,
    #                 "stressrun_results": stressrun_data
    #             })
    #     return Response(response_data, status=status.HTTP_200_OK)