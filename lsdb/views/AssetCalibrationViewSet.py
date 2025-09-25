from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from django.db import connection
from rest_framework.response import Response
from rest_framework.decorators import action

class AssetCalibrationViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCalibration.objects.all()
    serializer_class = AssetCalibrationSerializer

    def perform_create(self, serializer):
        if self.request.method=='POST':
            is_main_asset=self.request.data.get('is_main_asset')
            asset_type_id=self.request.data.get('asset_type')

            if is_main_asset==True :
                asset_calibration=serializer.save(is_sub_asset=False)
            elif is_main_asset==False and asset_type_id in [66]:
                asset_calibration=serializer.save(is_sub_asset=False,is_rack=True)
            elif is_main_asset==False:
                asset_calibration=serializer.save(is_sub_asset=True)
            
            asset = Asset.objects.create(
                name = asset_calibration.asset_name,
                description = asset_calibration.description,
                location_id = asset_calibration.location.id,
                last_action_datetime = asset_calibration.last_action_datetime,
                disposition_id = 16
            )
            asset_calibration.asset = asset 
            asset_calibration.save(update_fields=['asset'])
            if asset_calibration.asset_type:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO lsdb_asset_asset_types (asset_id, assettype_id) VALUES (%s, %s)",
                        [asset.id, asset_calibration.asset_type.id]
                    ) 
    @action(detail=False, methods=['post','get'])         
    def psr_subassets(self,request):
        if self.request.method=='GET':
            
            psr_subassets=AssetCalibration.objects.filter(is_main_asset=False,is_sub_asset=False,asset_type_id=66)
            for psr_subasset in psr_subassets:
                return Response({
                                    "sub_asset_name":psr_subasset.asset_name,
                                    "disposition_id":psr_subasset.disposition.id,
                                    "sub_asset_type":psr_subasset.asset_type.name
                                })
        elif self.request.method=='POST':
            asset_id=self.request.data.get('asset_id')
            sub_asset_ids=self.request.data.get('sub_asset_ids')

            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_id,sub_asset_id=sub_asset_id)
            return Response ({"detail":"Asset Linked"},status=200)

    @action(detail=False, methods=['post','get'])
    def link_asset_subasset(self,request):
        if self.request.method=='GET':
            sub_assets=AssetCalibration.objects.filter(is_main_asset=False)
            for subasset in sub_assets:
                return Response({
                    "sub_asset_name":subasset.asset_name,
                    "disposition_id":subasset.disposition.id,
                    "sub_asset_type":subasset.asset_type.name
                })
            
        elif self.request.method=='POST':
            asset_id=self.request.data.get('asset_id')
            sub_asset_ids=self.request.data.get('sub_asset_ids')

            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_id,sub_asset_id=sub_asset_id)
            return Response ({"detail":"Asset Linked"},status=200)
    
    
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
                "days_to_next_calibration": data["days_to_next_calibration"]
            }, status=200)
        except AssetCalibration.DoesNotExist:
            return Response({"error": "Asset Calibration not found"}, status=404)
        
    
    @action(detail=False, methods=['get'])
    def asset_list(self, request):
        is_main_asset = request.query_params.get('is_main_asset')
        if is_main_asset is None:
            return Response({"error": "is_main_asset parameter is required"}, status=400)
        assets = AssetCalibration.objects.filter(is_main_asset=is_main_asset)
        serializer = self.get_serializer(assets, many=True) 
        return Response(serializer.data, status=200)