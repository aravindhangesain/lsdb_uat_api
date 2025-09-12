from rest_framework import viewsets
from lsdb.serializers import *
from lsdb.models import *
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError, transaction
from django_filters import rest_framework as filters
from datetime import datetime





class AssetSubAssetFilter(filters.FilterSet):
    class Meta:
        model = AssetSubAsset
        fields = ['asset_id']


class AssetSubAssetViewSet(viewsets.ModelViewSet):
    
    queryset = AssetSubAsset.objects.all()
    serializer_class = AssetSubAssetSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssetSubAssetFilter
    
    @transaction.atomic
    @action(detail=False, methods=['get','post'])
    def assign_subasset(self, request):
        if request.method == 'POST':
            asset_id=request.data.get('asset_id')
            sub_asset_ids=request.data.get('sub_asset_ids')

            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_id, sub_asset_id=sub_asset_id)
            return Response({"status": "sub-assets assigned successfully"})
        
        return Response({"status": "use POST method to assign sub-assets to an asset"})
    
    @transaction.atomic
    @action(detail=False, methods=['get','post'])
    def stress_run(self,request):
        if request.method == 'POST':
            asset_id=request.data.get('asset_id')
            sub_asset_ids=request.data.get('sub_asset_ids')
            step_result_ids=request.data.get('step_result_ids') 
            run_name=request.data.get('run_name')
            comment=request.data.get('comment')

            for step_result_id in step_result_ids:
                step_result=StepResult.objects.get(id=step_result_id)
                procedure_result_id=step_result.procedure_result_id


                if step_result.name=='Test Start' and SubAsset.objects.filter(id__in=sub_asset_ids,disposition_id=[16,None]) and not StressRunResult.objects.filter(step_result_id=step_result_id):
                    stress_run_result=StressRunResult.objects.create(run_name=run_name,
                                                                    asset_id=asset_id,
                                                                    step_result_id=step_result_id,
                                                                    procedure_result_id=procedure_result_id,
                                                                    user_id=request.user.id,
                                                                    run_date=datetime.now(),
                                                                    comment=comment
                                                                    )
                    
                    
                
                elif step_result.name=='Test Resume' and StressRunResult.objects.filter(step_result__procedure_result_id=procedure_result_id).exists(): 
                    stress_run_result=StressRunResult.objects.create(run_name=run_name,
                                                                    asset_id=asset_id,
                                                                    step_result_id=step_result_id,
                                                                    procedure_result_id=procedure_result_id,
                                                                    user_id=request.user.id,
                                                                    run_date=datetime.now(),
                                                                    comment=comment
                                                                    )
                else:
                    return Response({"Cannot proceed with stress run. Ensure that all selected sub-assets are Available."})

            for sub_asset_id in sub_asset_ids:
                StressRunDetails.objects.create(sub_asset_id=sub_asset_id,stress_run_result_id=stress_run_result.id)
                sub_asset=SubAsset.objects.get(id=sub_asset_id)
                if sub_asset.disposition==20:
                    sub_asset.disposition=20
                    sub_asset.save()
                    
            return Response({"status": "stress run recorded successfully"})
        return Response({"status": "use POST method to record stress run"})
