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
    
    @action(detail=False, methods=['get','post'])
    def get_linked_subassets(self,request):
        if self.request.method=='GET':
            asset_id=request.query_params.get('asset_id')
            if AssetSubAsset.objects.filter(asset_id=asset_id).exists():
                linked_sub_assets=AssetSubAsset.objects.get(asset_id=asset_id)
                serializer=AssetSubAssetSerializer(linked_sub_assets,many=True)
                return Response(serializer.data)
            else:
                return Response({"status":"No sub-assets linked to this asset"})
        return Response({"status": "use GET method to fetch linked sub-assets for an asset"})

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


                if step_result.name=='Test Start' and AssetCalibration.objects.filter(id__in=sub_asset_ids,disposition_id__in=[16,None]) and not StressRunResult.objects.filter(step_result_id=step_result_id).exists():
                    stress_run_result=StressRunResult.objects.create(run_name=run_name,
                                                                    asset_id=asset_id,
                                                                    step_result_id=step_result_id,
                                                                    procedure_result_id=procedure_result_id,
                                                                    user_id=request.user.id,
                                                                    run_date=datetime.now(),
                                                                    comment=comment,
                                                                    stress_name=step_result.name
                                                                    )
                                                                    

                
                elif step_result.name=='Test Pause' and StressRunResult.objects.filter(step_result__procedure_result_id=procedure_result_id).exists():
                    if StressRunResult.objects.filter(stress_name='Test Start',procedure_result_id=step_result.procedure_result_id).exists():
                        prev_run=StressRunResult.objects.filter(stress_name='Test Start',procedure_result_id=step_result.procedure_result_id).first()
                        stress_run_result=StressRunResult.objects.create(run_name=prev_run.run_name,
                                                                        asset_id=asset_id,
                                                                        step_result_id=step_result_id,
                                                                        procedure_result_id=procedure_result_id,
                                                                        user_id=request.user.id,
                                                                        run_date=datetime.now(),
                                                                        # comment=comment,
                                                                        stress_name=step_result.name
                                                                        )  
                    
                
                elif step_result.name=='Test Resume' and StressRunResult.objects.filter(step_result__procedure_result_id=procedure_result_id).exists(): 
                    stress_run_result=StressRunResult.objects.create(run_name=run_name,
                                                                    asset_id=asset_id,
                                                                    step_result_id=step_result_id,
                                                                    procedure_result_id=procedure_result_id,
                                                                    user_id=request.user.id,
                                                                    run_date=datetime.now(),
                                                                    comment=comment,
                                                                    stress_name=step_result.name
                                                                    )
                elif step_result.name=='Test End' and StepResult.objects.filter(step_result_id=step_result_id).exists():
                    
                    if StressRunResult.objects.filter(stress_name='Test Resume',procedure_result_id=step_result.procedure_result_id).exists():
                        prev_run=StressRunResult.objects.filter(stress_name='Test Resume',procedure_result_id=step_result.procedure_result_id).first()
                        stress_run_result=StressRunResult.objects.create(run_name=prev_run.run_name,
                                                                        asset_id=asset_id,
                                                                        step_result_id=step_result_id,
                                                                        procedure_result_id=procedure_result_id,
                                                                        user_id=request.user.id,
                                                                        run_date=datetime.now(),
                                                                        # comment=comment,
                                                                        stress_name=step_result.name
                                                                        )
                    else:
                        prev_run=StressRunResult.objects.filter(stress_name='Test Start',procedure_result_id=step_result.procedure_result_id).first()
                        stress_run_result=StressRunResult.objects.create(run_name=prev_run.run_name,
                                                                        asset_id=asset_id,
                                                                        step_result_id=step_result_id,
                                                                        procedure_result_id=procedure_result_id,
                                                                        user_id=request.user.id,
                                                                        run_date=datetime.now(),
                                                                        # comment=comment,
                                                                        stress_name=step_result.name
                                                                        )

                        

                else:
                    return Response({"Cannot proceed with stress run. Ensure that all selected sub-assets are Available."})

            for sub_asset_id in sub_asset_ids:
                StressRunDetails.objects.create(sub_asset_id=sub_asset_id,stress_run_result_id=stress_run_result.id)
                sub_asset=AssetCalibration.objects.get(id=sub_asset_id)
                if sub_asset:
                    sub_asset.disposition=20
                    sub_asset.save()
                    
            return Response({"status": "stress run recorded successfully"})
        return Response({"status": "use POST method to record stress run"})
