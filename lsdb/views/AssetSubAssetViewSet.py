from rest_framework import viewsets,status
from lsdb.serializers import *
from lsdb.models import *
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError, transaction
from django_filters import rest_framework as filters
from datetime import datetime
from django.db.models import Q



class AssetSubAssetViewSet(viewsets.ModelViewSet):
    
    queryset = AssetSubAsset.objects.all()
    serializer_class = AssetSubAssetSerializer
    
    def list(self, request, *args, **kwargs):
        asset_id = request.query_params.get("asset_id")
        if asset_id:
            calibration_ids = AssetCalibration.objects.filter(
                asset_id=asset_id
            ).values_list("id", flat=True)

            linked_qs = AssetSubAsset.objects.filter(asset_id__in=calibration_ids)
            if not linked_qs.exists():
                return Response(
                    {"status": "No sub-assets linked to this asset"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = self.get_serializer(linked_qs, many=True)
            return Response({"results": serializer.data})

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"results": serializer.data})  
            
    
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

            asset_calibration=AssetCalibration.objects.filter(asset_id=asset_id).first()
            for step_result_id in step_result_ids:
                step_result=StepResult.objects.get(id=step_result_id)
                procedure_result_id=step_result.procedure_result_id


                if step_result.step_definition.id==6:
                        stress_run_result=StressRunResult.objects.create(run_name=run_name,
                                                                        asset_id=asset_calibration.id,
                                                                        step_result_id=step_result_id,
                                                                        procedure_result_id=procedure_result_id,
                                                                        user_id=request.user.id,
                                                                        run_date=datetime.now(),
                                                                        comment=comment,
                                                                        stress_name=step_result.name,
                                                                        disposition=Disposition.objects.get(id=7)
                                                                        )
                    
                                                                    

                
                elif step_result.name=='Test Pause' :
                    
                        prev_run1=StressRunResult.objects.filter(stress_name='Test Start',procedure_result_id=step_result.procedure_result_id).first()
                        
                        prev_run1.disposition=Disposition.objects.get(id=20)
                        prev_run1.save()
                        stress_run_result=StressRunResult.objects.create(run_name=prev_run1.run_name,
                                                                        asset_id=asset_calibration.id,
                                                                        step_result_id=step_result_id,
                                                                        procedure_result_id=procedure_result_id,
                                                                        user_id=request.user.id,
                                                                        run_date=datetime.now(),
                                                                        # comment=comment,
                                                                        stress_name=step_result.name,
                                                                        disposition=Disposition.objects.get(id=7)
                                                                        )
                          
                    
                
                elif step_result.name=='Test Resume': 
                    prev_run4=StressRunResult.objects.filter(stress_name='Test Pause',step_result__procedure_result_id=procedure_result_id).first()
                    prev_run4.disposition=Disposition.objects.get(id=20)
                    prev_run4.save()
                    stress_run_result=StressRunResult.objects.create(run_name=run_name,
                                                                    asset_id=asset_calibration.id,
                                                                    step_result_id=step_result_id,
                                                                    procedure_result_id=procedure_result_id,
                                                                    user_id=request.user.id,
                                                                    run_date=datetime.now(),
                                                                    comment=comment,
                                                                    stress_name=step_result.name,
                                                                    disposition=Disposition.objects.get(id=7)
                                                                    )
                    
                elif step_result.name=='Test End':
                    
                    
                        if StressRunResult.objects.filter(stress_name='Test Resume',procedure_result_id=step_result.procedure_result_id).exists():
                            prev_run2=StressRunResult.objects.filter(stress_name='Test Resume',procedure_result_id=step_result.procedure_result_id).first()
                            prev_run2.disposition=Disposition.objects.get(id=20)
                            prev_run2.save()
                            stress_run_result=StressRunResult.objects.create(run_name=prev_run2.run_name,
                                                                            asset_id=asset_calibration.id,
                                                                            step_result_id=step_result_id,
                                                                            procedure_result_id=procedure_result_id,
                                                                            user_id=request.user.id,
                                                                            run_date=datetime.now(),
                                                                            # comment=comment,
                                                                            stress_name=step_result.name,
                                                                            disposition=Disposition.objects.get(id=20)
                                                                            )
                        else:
                            prev_run3=StressRunResult.objects.filter(stress_name='Test Start',procedure_result_id=step_result.procedure_result_id).first()
                            prev_run3.disposition=Disposition.objects.get(id=20)
                            prev_run3.save()
                            stress_run_result=StressRunResult.objects.create(run_name=prev_run3.run_name,
                                                                            asset_id=asset_calibration.id,
                                                                            step_result_id=step_result_id,
                                                                            procedure_result_id=procedure_result_id,
                                                                            user_id=request.user.id,
                                                                            run_date=datetime.now(),
                                                                            # comment=comment,
                                                                            stress_name=step_result.name,
                                                                            disposition=Disposition.objects.get(id=20)
                                                                            )

                        

                
            if step_result.name=='Test Start' or step_result.name=='Test Resume':
                
                if AssetCalibration.objects.filter(asset_id=asset_id,is_main_asset=True).exists():
                    asset=AssetCalibration.objects.get(asset_id=asset_id,is_main_asset=True)
                    asset.disposition=Disposition.objects.get(id=7)
                    asset.save()
                    for sub_asset_id in sub_asset_ids:
                        print("sub_asset_id",sub_asset_id)
                        # print("stress_run_result_id",stress_run_result.id)
                        StressRunDetails.objects.create(sub_asset_id=sub_asset_id,stress_run_result_id=stress_run_result.id)
                        sub_asset=AssetCalibration.objects.get(id=sub_asset_id)
                        if sub_asset:
                            sub_asset.disposition=Disposition.objects.get(id=7)
                            sub_asset.save()
                        if AssetLastActionDetails.objects.filter(asset_id=asset_id).exists():
                            last_action = AssetLastActionDetails.objects.get(asset_id=asset_id)
                            if step_result.name == 'Test Start':
                                last_action.action_name = 'Stress Started'
                            else:
                                last_action.action_name = 'Stress Resumed'
                            last_action.action_datetime = datetime.now()
                            last_action.user_id = request.user.id
                            last_action.save()
                        else:
                            action_name = 'Stress Started' if step_result.name == 'Test Start' else 'Stress Resumed'
                            AssetLastActionDetails.objects.create(
                                asset_id=asset_id,
                                action_name=action_name,
                                action_datetime=datetime.now(),
                                user_id=request.user.id
                            )


                    return Response({"status": "stress run recorded successfully"})
            
            elif step_result.name=='Test Pause':
                asset=AssetCalibration.objects.get(asset_id=asset_id,is_main_asset=True)
                asset.disposition=Disposition.objects.get(id=7)
                asset.save()
                if StressRunResult.objects.filter(stress_name='Test Start',asset_id=asset_calibration.id,procedure_result_id=step_result.procedure_result_id).exists():
                    start_run=StressRunResult.objects.get(stress_name='Test Start',asset_id=asset_calibration.id,procedure_result_id=step_result.procedure_result_id)
                    start_sub_asset_ids=StressRunDetails.objects.filter(stress_run_result_id=start_run.id,sub_asset_id=asset_calibration.id).values_list('sub_asset_id',flat=True)
                    for subasset_id in start_sub_asset_ids:
                        
                        StressRunDetails.objects.create(sub_asset_id=subasset_id,stress_run_result_id=stress_run_result.id)
                        sub_asset=AssetCalibration.objects.get(id=subasset_id)
                        if sub_asset:
                            sub_asset.disposition=Disposition.objects.get(id=7)
                            sub_asset.save()
                        if AssetLastActionDetails.objects.filter(asset_id=asset_id).exists():
                            last_action=AssetLastActionDetails.objects.get(asset_id=asset_id)
                            last_action.action_name='Stress Paused'
                            last_action.action_datetime=datetime.now()
                            last_action.user_id=request.user.id
                            last_action.save()
                        else:
                            AssetLastActionDetails.objects.create(
                                                                  asset_id=asset_id,
                                                                  action_name='Stress Paused',
                                                                  action_datetime=datetime.now(),
                                                                  user_id=request.user.id
                                                                )
                    return Response({"status": "stress run recorded successfully"})

            
            elif step_result.name=='Test End':
                if AssetCalibration.objects.filter(asset_id=asset_id,is_main_asset=True).exists():
                    asset=AssetCalibration.objects.get(asset_id=asset_id,is_main_asset=True)
                    asset.disposition=Disposition.objects.get(id=16)
                    asset.save()
                    if StressRunResult.objects.filter(stress_name='Test Resume',asset_id=asset_calibration.id,procedure_result_id=step_result.procedure_result_id).exists():
                        resume_run=StressRunResult.objects.get(stress_name='Test Resume',asset_id=asset_calibration.id)
                        resume_sub_asset_ids=StressRunDetails.objects.filter(stress_run_result_id=resume_run.id,sub_asset_id=asset_calibration.id).values_list('sub_asset_id',flat=True)   
                        for sub_asset_id in resume_sub_asset_ids:
                            StressRunDetails.objects.create(sub_asset_id=sub_asset_id,stress_run_result_id=stress_run_result.id)
                            sub_asset=AssetCalibration.objects.get(id=sub_asset_id)
                            if sub_asset:
                                sub_asset.disposition=Disposition.objects.get(id=16)
                                sub_asset.save()
                                if AssetLastActionDetails.objects.filter(asset_id=asset_id).exists():
                                    last_action=AssetLastActionDetails.objects.get(asset_id=asset_id)
                                    last_action.action_name='stress exit'
                                    last_action.action_datetime=datetime.now()
                                    last_action.user_id=request.user.id
                                    last_action.save()
                                else:
                                    AssetLastActionDetails.objects.create(
                                                                        asset_id=asset_id,
                                                                        action_name='stress exit',
                                                                        action_datetime=datetime.now(),
                                                                        user_id=request.user.id
                                                                        )
                        return Response({"status": "stress run recorded successfully"})
                            
                    elif StressRunResult.objects.filter(stress_name='Test Start',asset_id=asset_calibration.id,procedure_result_id=step_result.procedure_result_id).exists():
                        start_run=StressRunResult.objects.get(stress_name='Test Start',asset_id=asset_calibration.id,procedure_result_id=step_result.procedure_result_id)
                        start_sub_asset_ids=StressRunDetails.objects.filter(stress_run_result_id=start_run.id,sub_asset_id=asset_calibration.id).values_list('sub_asset_id',flat=True)
                        for subasset_id in start_sub_asset_ids:
                            
                            StressRunDetails.objects.create(sub_asset_id=subasset_id,stress_run_result_id=stress_run_result.id)
                            sub_asset=AssetCalibration.objects.get(id=subasset_id)
                            if sub_asset:
                                sub_asset.disposition=Disposition.objects.get(id=16)
                                sub_asset.save()
                                if AssetLastActionDetails.objects.filter(asset_id=asset_id).exists():
                                    last_action=AssetLastActionDetails.objects.get(asset_id=asset_id)
                                    last_action.action_name='Stress Exit'
                                    last_action.action_datetime=datetime.now()
                                    last_action.user_id=request.user.id
                                    last_action.save()
                                else:
                                    AssetLastActionDetails.objects.create(
                                                                        asset_id=asset_id,
                                                                        action_name='Stress Exit',
                                                                        action_datetime=datetime.now(),
                                                                        user_id=request.user.id
                                                                        )
                        return Response({"status": "stress run recorded successfully"})
            
            else:
                return Response({"status": "stress run recorded successfully"})
                    

        return Response({"status": "use POST method to record stress run"})
