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
            step_result_id=request.data.get('step_result_id')

            stress_run_result=StressRunResult.objects.create(asset_id=asset_id,step_result_id=step_result_id,user_id=request.user.id,run_date=datetime.now())

            for sub_asset_id in sub_asset_ids:
                StressRunDetails.objects.create(sub_asset_id=sub_asset_id,stress_run_result_id=stress_run_result.id)
            return Response({"status": "stress run recorded successfully"})
        return Response({"status": "use POST method to record stress run"})
