from django.utils import timezone   
from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from django.db import connection
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime


class AssetCalibrationViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCalibration.objects.all()
    serializer_class = AssetCalibrationSerializer
    # pagination_class = None

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()

        if 'disposition' in request.data:
            if AssetLastActionDetails.objects.filter(asset_id=pk).exists():
                last_action = AssetLastActionDetails.objects.get(asset_id=pk)
                last_action.action_name='Disposition Updated'
                last_action.action_datetime=datetime.now()
                last_action.user_id=request.user.id
                last_action.save()
            else:
                AssetLastActionDetails.objects.create(
                                                    asset_id=pk,
                                                    action_name='Disposition Updated',
                                                    action_datetime=datetime.now(),
                                                    user_id=request.user.id
                                                    )
                

        return super().partial_update(request, *args, **kwargs)


    def perform_create(self, serializer):
        if self.request.method == 'POST':
            # Convert string/None to proper boolean
            is_main_asset_str = self.request.data.get('is_main_asset')
            asset_type_id = self.request.data.get('asset_type')

            # handle possible string input like "true"/"false"
            is_main_asset = str(is_main_asset_str).lower() == 'true'

            # Always start with a default to avoid UnboundLocalError
            asset_calibration = None

            if is_main_asset:
                asset_calibration = serializer.save(
                    is_sub_asset=False, is_rack=False, disposition_id=16
                )
            elif not is_main_asset and asset_type_id in [66]:
                asset_calibration = serializer.save(
                    is_sub_asset=False, is_rack=True, disposition_id=16
                )
            elif is_main_asset is False:
                asset_calibration = serializer.save(
                    is_sub_asset=True, is_rack=False, disposition_id=16
                )

            if not asset_calibration:
                # No branch matched -> raise clear error
                raise ValueError(
                    "Could not create AssetCalibration: invalid is_main_asset or asset_type"
                )

            # Create linked Asset
            asset = Asset.objects.create(
                name=asset_calibration.asset_name,
                description=asset_calibration.description,
                location_id=asset_calibration.location.id,
                last_action_datetime=asset_calibration.last_action_datetime,
                disposition_id=16
            )

            asset_calibration.asset = asset
            asset_calibration.save(update_fields=['asset'])

            if asset_calibration.asset_type:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO lsdb_asset_asset_types (asset_id, assettype_id)
                        VALUES (%s, %s)
                        """,
                        [asset.id, asset_calibration.asset_type.id]
                    )
    @action(detail=False, methods=['post','get'])         
    def psr_subassets(self,request):
        if self.request.method=='GET':
            
            psr_subassets=AssetCalibration.objects.filter(is_main_asset=False,is_sub_asset=True,is_rack=False,asset_type_id=23)
            print(psr_subassets)
            serializer = self.get_serializer(psr_subassets, many=True)
            data = serializer.data
            filtered_data = [
                {k: d[k] for k in ("id", "asset_name", "asset_number","asset_type","asset_type_name","disposition_id",
                                   "is_calibration_date","asset_next_calibration","in_use","is_calibration")} for d in data
            ]            
            return Response(filtered_data, status=200)
            
        elif self.request.method=='POST':
            asset_calibration_id=self.request.data.get('asset_calibration_id')
            sub_asset_ids=self.request.data.get('sub_asset_ids')

            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_calibration_id,sub_asset_id=sub_asset_id,linked_date=timezone.now())
            return Response ({"detail":"Asset Linked"},status=200)

    @action(detail=False, methods=['post','get','put','delete'])
    def link_asset_subasset(self,request):
        if self.request.method=='GET':
            is_main_asset = request.query_params.get('is_main_asset')
            if is_main_asset is None:
                return Response({"error": "is_main_asset parameter is required"}, status=400)
            if isinstance(is_main_asset, str):
                is_main_asset = is_main_asset.lower() in ['true', '1', 'yes']
            assets = AssetCalibration.objects.filter(is_main_asset=is_main_asset)
            serializer = self.get_serializer(assets, many=True) 
            return Response(serializer.data, status=200)
            
        elif self.request.method=='POST':
            asset_calibration_id=self.request.data.get('asset_calibration_id')
            sub_asset_ids=self.request.data.get('sub_asset_ids')

            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_calibration_id,sub_asset_id=sub_asset_id,linked_date=timezone.now())
            return Response ({"detail":"Asset Linked"},status=200)
        
        elif self.request.method=='PUT':
            asset_calibration_id=request.data.get('asset_calibration_id')
            sub_asset_ids=request.data.get('sub_asset_ids')
            AssetSubAsset.objects.filter(asset_id=asset_calibration_id).delete()
            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_calibration_id,sub_asset_id=sub_asset_id,linked_date=timezone.now())
            return Response ({"detail":"Asset Re-Linked"},status=200)
        
        elif self.request.method=='DELETE':
            asset_calibration_id= request.query_params.get('asset_calibration_id')
            AssetSubAsset.objects.filter(asset_id=asset_calibration_id).delete()
            return Response ({"detail":"Asset Unlinked"},status=200)

    @action(detail=False, methods=['get'])
    def edit_asset_get(self, request):
        asset_calibration_id = request.query_params.get('id')
        if not asset_calibration_id:
            return Response({"error": "Asset Calibration ID is required"}, status=400)

        try:
            # all sub assets
            asset_calibrations = AssetCalibration.objects.filter(is_sub_asset=True)

            # find linked sub-assets for the given asset
            linked_subassets = AssetSubAsset.objects.filter(asset_id=asset_calibration_id)
            linked_subasset_ids = {subasset.sub_asset.id for subasset in linked_subassets}

            # serialize all sub-assets
            serializer = self.get_serializer(asset_calibrations, many=True)
            serialized_data = serializer.data

            # add is_linked field
            output = []
            for asset in serialized_data:
                asset_id = asset.get("id")
                is_linked = asset_id in linked_subasset_ids
                asset["is_linked"] = is_linked
                output.append(asset)

            return Response(output, status=200)

        except AssetCalibration.DoesNotExist:
            return Response({"error": "Asset Calibration not found"}, status=404)
                    
                    


            
            
                   
        
        
    @action(detail=False, methods=['get'])
    def asset_info(self, request):
        asset_id = request.query_params.get('asset_id')
        if not asset_id:
            return Response({"error": "Asset ID is required"}, status=400)
        try:
            asset_calibration = AssetCalibration.objects.get(asset_id=asset_id)
            serializer = self.get_serializer(asset_calibration)
            data = serializer.data
            return Response({
                "last_calibrated_date": data["last_calibrated_date"],
                "next_calibration_date": data["next_calibration_date"],
                "asset_name": data["asset_name"],
                "calibration_days": data["calibration_days"],
                "is_calibration": data["is_calibration"],
                "days_to_next_calibration": data["asset_next_calibration"]
            }, status=200)
        except AssetCalibration.DoesNotExist:
            return Response({"error": "Asset Calibration not found"}, status=404)
        
    @action(detail=False, methods=['get', ],
            serializer_class=DispositionCodeListSerializer)
    def asset_dispositions(self, request, pk=None):
        self.context = {'request': request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(name='asset_management'),many=False,context={'request': request})
        return Response(serializer.data)
        
    
    # @action(detail=False, methods=['get'])
    # def asset_list(self, request):
    #     is_main_asset = request.query_params.get('is_main_asset')
    #     if is_main_asset is None:
    #         return Response({"error": "is_main_asset parameter is required"}, status=400)
    #     assets = AssetCalibration.objects.filter(is_main_asset=is_main_asset)
    #     serializer = self.get_serializer(assets, many=True) 
    #     return Response(serializer.data, status=200)