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