from rest_framework import viewsets
from lsdb.serializers import *
from lsdb.models import *
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import IntegrityError, transaction





class AssetSubAssetViewSet(viewsets.ModelViewSet):
    
    queryset = AssetSubAsset.objects.all()
    serializer_class = AssetSubAssetSerializer

    @transaction.atomic
    @action(detail=False, methods=['get','post'])
    def assign_subasset(self, request,):
        asset_id=request.data.get('asset_id')
        sub_asset_ids=request.data.get('sub_asset_ids')

        for sub_asset_id in sub_asset_ids:
            AssetSubAsset.objects.create(asset_id=asset_id, sub_asset_id=sub_asset_id)
        return Response({"status": "sub-assets assigned successfully"})
